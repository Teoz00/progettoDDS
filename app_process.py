from graph_gen import Graph
from pp2p import PerfectPointToPointLink
from consensus import Consensus
from pfd import PerfectFailureDetector

import threading
import ast
import uuid
import time

class ApplicationProcess:
    def __init__(self, my_id, my_addr, neighbors, number_node, num_apps, base_port, stop_event):

        self.id = my_id

        self.my_addr = my_addr
        self.neighbors = neighbors
        self.corrects = []
        self.correct_rsms = []
        self.num_nodes = number_node
        self.num_apps = num_apps
        self.delay = 0.005

        # if(self.id == 2):
        #     self.delay = 0.20

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

        self.pfd = PerfectFailureDetector()
        self.cons = Consensus(self.id, num_apps)

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

        for i in range(0, self.num_apps):
            if(i != self.id):
                self.corrects.append(i)

        for i in range(0, self.num_nodes):
            self.correct_rsms.append(i)

        # self.subgraph.set_same_input_rsm(None)

        # my_id, my_addr, neighbors to be used for communication between ApplicacionProcesses

    def app_proc_listen_msg(self, link):
        while(not(self.stop_event.is_set())):
            message = link.recv()

            if ((message is not None) and (message not in self.messageLog)):
                print(f"ApplicationProcess {self.id} > recv {message}")
                self.messageLog.append(message)

                reconstructed_payload = ast.literal_eval(message)        
                print(reconstructed_payload)
                
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

                match type:
                    case "SIMPLE":
                        if(self.links[str(origin)] == link):

                            if(msg == "HeartBeatRequest"):
                                self.app_proc_send_to("ACK", origin, "HeartBeatReply", message_id, self.id)
                            else:
                                msg = msg.split(", ")
                                if(msg[0] == "CONSENSUS"):
                                    if(self.cons.handle_msg(msg, message_id, origin) == True):
                                        self.app_ask_consensus_lieutant(message_id, origin, msg[2])
                                    else:
                                        if(self.cons.am_I_a_commander(message_id)):
                                            print(f"ApplicationProcess {self.id} - Commander : recieved {msg[2]} from {origin}")
                                        
                                        # print(f"ApplicationProcess {self.id} > checking values on {message_id} : {self.cons.check_values(message_id)} - {(self.cons.already_chosen(message_id))} ")
                                        
                                        if(self.cons.check_values(message_id)) and not(self.cons.already_chosen(message_id)):
                                            val = self.cons.choose_value(message_id)
                                            if(not(self.cons.am_I_a_commander(message_id))):
                                                self.app_proc_send_to(type, self.cons.get_commander(message_id), str('["CONSENSUS", "LIEUTANT", ' + str(val) + ', ]'), message_id, self.id)


                                # self.app_proc_send_to("ACK", origin, msg, message_id, self.id)
                    
                    case "ACK":
                        if message_id not in self.received_acks:
                            self.received_acks.update({message_id : []})

                        if (msg == "HeartBeatReply"):
                            self.pfd.append_ack(message_id, origin)
        
                        if(origin not in self.received_acks[message_id]):
                            self.received_acks[message_id].append(origin)
                            #print(f"ApplicationProcess {self.id} : acks-status for {message_id} -> {self.received_acks[message_id]}")

            time.sleep(self.delay)


    def app_proc_send_to(self, type, peer_id, msg, msg_id, origin):        
        if(msg_id == None):
            msg_id = str(uuid.uuid4())
        else:
            if((type, msg, msg_id) in self.sent_to[peer_id]):
                print(f"ApplicationProcess {self.id} > [{type}, {msg}, {msg_id}] already sent to {peer_id}")
                return

        try:
            self.vectorClock[self.id] += 1
            print(f"ApplicationProcess {self.id} > sending [{type, peer_id, msg, msg_id, self.vectorClock, origin}] to {peer_id}")
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

    def app_proc_broadcast(self, msg, id):
        print(f"Node {self.id} - corrects : {self.corrects}")
        if(id == None):
            id == str(uuid.uuid4())

        for elem in self.corrects:
            self.app_proc_send_to("SIMPLE", elem, msg, id, self.id)

    def get_port_counter(self):
        pc = self.subgraph.get_port_counter()
        return pc
    
    def get_rsm_consensus(self, id, msg_id, msg):
        cons = []
        print("AppProc ", self.id, " > self.correct_rsns : ", self.correct_rsms)
        print({str(id) in self.correct_rsms})
        if(id in self.correct_rsms):
            cons.append(self.subgraph.ask_consensus(id, msg_id, msg))
            # self.subgraph.nodes[id].asking_for_consensus_commander(msg)
        
        print(f"ApplicationProcess {self.id} > consensus list {cons}")

        return cons

    def is_chosen(self, msg_id):
        return self.cons.get_val(msg_id)

    def get_num_nodes(self):
        return self.subgraph.get_size()
    
    def get_vc(self):
        return self.vectorClock

    def get_app_consensus(self, msg_id):
        pass

    def app_ask_consensus_commander(self, id, value):
        if (id == None):
            id = str(uuid.uuid4())

        message = ("CONSENSUS, " + "COMMANDER, " + (str(value)))
        self.app_proc_broadcast(message, id)
        self.cons.set_value(id, value)

    def app_ask_consensus_lieutant(self, msg_id, commander, value):
        if(self.cons.get_commander(msg_id) == None):
            print(f"ApplicationProcess {self.id} : error while checking for commander for message {msg_id}")

        else:
            msg = ("CONSENSUS, " + "LIEUTANT, "  + value)
            if(msg_id == None):
                msg_id == str(uuid.uuid4())

            if(msg_id not in self.received_acks):
                self.received_acks[msg_id] = []

            print("starting lieutant consensus")
            self.app_proc_broadcast(msg, msg_id)
               
    def app_proc_pfd_caller(self, event):

        msg_id = str(uuid.uuid4())
        self.pfd.start_pfd(self.corrects, msg_id, self.delay * (3 * self.num_apps))
        self.app_proc_broadcast("HeartBeatRequest", msg_id)

        time.sleep(self.delay * (3 * self.num_apps + 1))

        if(self.pfd.get_flag() == "AUG_DELAY"):
            print(f"ApplicationProcess {self.id } - Restarting app_proc_pfd_caller...")
            return self.app_proc_pfd_caller(event)
        
        elif(self.pfd.get_flag() == True):
            # print(f"pfd.get_flag = {self.pfd.get_flag()} - corrects : {self.pfd.get_new_corrects()}")
            tmp = self.corrects
            self.corrects = self.pfd.get_new_corrects()
            # print(f"ApplicationProcess {self.id} > new corrects: {self.corrects} vs old corrects : {tmp}")
            event.set()
            return self.corrects

    def get_new_corrects(self):
        ev = threading.Event()
        ret = self.app_proc_pfd_caller(ev)

        while(not ev.is_set()):
            time.sleep(0.5)

        return ret

    def print_cons(self):
        # print("print_cons invoked")
        self.subgraph.print_agreed_values()

    def check_faulty_rsms(self, event):
        res = self.subgraph.check_faulty_rsms()
        print(f"\nApplicationProcess {self.id} > res : {res}")

        voted_nodes = {}
        for elem in self.subgraph.nodes_list:
            voted_nodes.update({elem : 0})
            voted_nodes[elem] += 1
        
        for elem in res:
            # id : elem[0], its corrects: elem[1]
            voted_nodes[elem] += 1
        
        print(f"ApplicationProcess {self.id} > voted_nodes : {voted_nodes}\n")
        threshold = min(voted_nodes.values())

        n = len(self.correct_rsms)

        self.correct_rsms = []
        for elem in voted_nodes:
            if(voted_nodes[elem] > threshold):
                if(elem not in self.correct_rsms):
                    self.correct_rsms.append(elem)

        self.correct_rsms.sort()
        n = len(self.correct_rsms)
        
        for elem in self.correct_rsms:
            self.subgraph.nodes[elem].cons.set_num_nodes(n)
            self.subgraph.nodes[elem].set_new_corrects(self.correct_rsms)

        print(f"ApplicationProcess {self.id} > new corrects : {self.correct_rsms}")

        event.set()
        return self.correct_rsms
    
    def app_proc_rsm_input(self, event_set):

        self.subgraph.set_input_rsm_ensemble(event_set)
    # TODO may need to be completed

    def plot_graph(self):
        self.subgraph.plot_graph()

    def cleanup(self):
        self.subgraph.cleanup()