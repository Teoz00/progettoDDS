from graph_gen import Graph
from pp2p import PerfectPointToPointLink

import threading
import ast
import uuid

class ApplicationProcess:
    def __init__(self, my_id, my_addr, neighbors, number_node, num_apps, base_port, stop_event):

        self.id = my_id

        self.my_addr = my_addr
        self.neighbors = neighbors
        self.num_nodes = number_node
        self.num_apps = num_apps

        self.running = False
        self.listener_threads = {}
        self.links = {}
        
        self.subgraph = Graph(my_id, number_node, base_port, stop_event)
        self.consensus = []

        self.messageLog = []
        self.sent_to = {}

        for elem in self.neighbors:
            self.sent_to.update({elem['neigh']: []})
                
        self.received_acks = {}
            
        self.vectorClock = [0] * (self.num_apps)

        self.stop_event = stop_event

        for elem in neighbors:
            link_addr = f"{my_addr}:{elem['port']}"
            neigh_addr = f"{elem['neigh_ip']}:{elem['neigh_port']}"
            self.links.update({str(elem['neigh']): PerfectPointToPointLink(link_addr, neigh_addr)})

            try:
                self.running = True
                thr = threading.Thread(target=self.app_proc_listen_msg, args=(self.links[str(elem['neigh'])],))
                self.listener_threads.update({elem['neigh']: thr})
                self.listener_threads[elem['neigh']].start()
            
            except Exception as e:
                print(f"Catched: {e} while starting thread at {self.id}:{elem['port']}")
                # self.cleanup()

        # self.subgraph.set_same_input_rsm(None)

        # my_id, my_addr, neighbors to be used for communication between ApplicacionProcesses

    def app_proc_listen_msg(self, link):
        while(not(self.stop_event.is_set())):
            message = link.recv()

            if ((message is not None) and (message not in self.messageLog)):
                print(f"ApplicationProcess {self.id} > recv {message}")
                self.messageLog.append(message)

                reconstructed_payload = ast.literal_eval(message)        
                
                type = reconstructed_payload[0]
                if type not in {"ACK", "SIMPLE"}:
                    print("Invalid message!!")
                    return

                msg = reconstructed_payload[1]
                message_id = reconstructed_payload[2]
                vc = reconstructed_payload[3]
                origin = reconstructed_payload[4]

                self.manage_vector_clock(vc)
                self.vectorClock[self.id] += 1

                FOUND = False

                match type:
                    case "SIMPLE":
                        if(self.links[str(origin)] == link):
                            self.app_proc_send_to("ACK", origin, msg, message_id, self.id)
                    
                    case "ACK":
                        if message_id not in self.received_acks:
                            self.received_acks.update({message_id : []})
                        
                        if(origin not in self.received_acks[message_id]):
                            self.received_acks[message_id].append(origin)
                            print(f"ApplicationProcess {self.id} : acks-status for {message_id} -> {self.received_acks[message_id]}")

    def app_proc_send_to(self, type, peer_id, msg, msg_id, origin):
        print(f"ApplicationProcess {self.id} > sending [{type, peer_id, msg, msg_id, self.vectorClock, origin}] to {peer_id}")
        
        if(msg_id == None):
            msg_id = str(uuid.uuid4())
        else:
            if((type, msg, msg_id) in self.sent_to[peer_id]):
                print(f"ApplicationProcess {self.id} > [{type}, {msg}, {msg_id}] already sent to {peer_id}")
                return
        
        try:
            self.vectorClock[self.id] += 1
            self.links[(str(peer_id))].send([type, msg, msg_id, self.vectorClock, self.id])
            self.messageLog.append(str([type, msg, msg_id, self.vectorClock, self.id]))
            self.sent_to[peer_id].append((type, msg, msg_id))
            
        except Exception as e:
            print(f"ApplicationProcess {self.id} - catched {e} while sending [{type}, {msg}, {msg_id}] to {peer_id}")

    def manage_vector_clock(self, vc):
        if(not(isinstance(vc, list))):
            vc = ast.literal_eval(vc)

        for i in range(0, self.num_apps):
            if(self.vectorClock[i] < vc[i]):
                self.vectorClock[i] = vc[i]

    def app_proc_broadcast(self, msg):
        msg_id = str(uuid.uuid4())
        for elem in self.neighbors:
            self.app_proc_send_to("SIMPLE", elem['neigh'], msg, msg_id, self.id)

    def get_port_counter(self):
        pc = self.subgraph.get_port_counter()
        return pc
    
    def get_consensus(self, id, msg_id, msg):
        cons = []
        if(id in self.subgraph.nodes):
            cons.append(self.subgraph.ask_consensus(id, msg_id, msg))
            # self.subgraph.nodes[id].asking_for_consensus_commander(msg)
        
        print(f"ApplicationProcess {self.id} > consensus list {cons}")
        return cons

    def get_num_nodes(self):
        return self.subgraph.get_size()
    
    def get_vc(self):
        return self.vectorClock

    def print_cons(self):
        # print("print_cons invoked")
        self.subgraph.print_agreed_values()

    def check_faulties(self,node_id):
        return self.subgraph.pfd_single_result(node_id)

    def plot_graph(self):
        self.subgraph.plot_graph()

    def cleanup(self):
        self.subgraph.cleanup()