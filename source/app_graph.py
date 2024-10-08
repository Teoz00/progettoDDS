from app_process import ApplicationProcess
from event_process import EventP
from LASKALSJ import LASKALSJ

import networkx as nx
import matplotlib.pyplot as plt
import uuid
import threading
import random
import time

###

class ApplicationGraph:
    def __init__(self, num_apps, t_byzantine):

        self.app_graph = nx.complete_graph(num_apps)
        # self.app_graph = nx.erdos_renyi_graph(n=num_apps, p=0.75, seed=42)
        self.stop_event = threading.Event()
        
        ip = "127.0.0.1"
        base_port = 49152
        port_counter = base_port

        self.app_nodes = {}
        self.corrects = self.app_graph.nodes()
        self.app_nodes_list = self.app_graph.nodes()
        self.port_map = {}
        detailed_app_nodes_list = {}

        self.consensus_events = {}
        self.stop_event = threading.Event()
        self.LASKALSJ = LASKALSJ(num_apps)

        # consensus for each message has an entry into a dedicated structure
        self.consensus_events = {}

        self.happened_events = {}
        self.timestamp = 0
        self.vector_clock = [0] * num_apps

        self.byz = t_byzantine

        for node in self.app_nodes_list:
            # self.consensus_events.update({node: threading.Event()})
            for neighbor in self.app_graph.neighbors(node):
                if (node, neighbor) not in self.port_map:
                    self.port_map[(node, neighbor)] = port_counter
                    self.port_map[(neighbor, node)] = port_counter + 1
                    port_counter += 2

        for node in self.app_nodes_list:
            # print(node)
            ports_for_node = []
            for (node1, node2), port in self.port_map.items():
                if node1 == node:
                    ports_for_node.append({"port": port, "neigh": node2})
              
            detailed_app_nodes_list[node] = {"id": node, "ip": ip, "ports": ports_for_node}
        
        nodes_per_subgraph = int(3 * int(t_byzantine) + 2)

        # self.consensus_events[detailed_app_nodes_list[node]['id']]

        for node in detailed_app_nodes_list:
            for elem in detailed_app_nodes_list[node]['ports']:
                neigh_id = elem['neigh']
                for neighbor in detailed_app_nodes_list[neigh_id]['ports']:
                    elem.update({"neigh_ip": ip})
                    if neighbor['neigh'] == node:
                        elem.update({"neigh_port": neighbor['port']})

            self.app_nodes[node] = ApplicationProcess(detailed_app_nodes_list[node]['id'], detailed_app_nodes_list[node]['ip'], detailed_app_nodes_list[node]['ports'], nodes_per_subgraph, num_apps, port_counter, self.LASKALSJ, self.stop_event)
            port_counter = self.app_nodes[node].get_port_counter()

    ######## PFD FOR RSMS #######

    def check_faulty_rsms_thread_starter(self, app_id, event, list_for_corrects):
        FOUND = False

        for elem in list_for_corrects:
            if(app_id == elem[0]):
                FOUND = True
                break
        
        if(not FOUND):
            val = [app_id, self.app_nodes[app_id].check_faulty_rsms(event)]
            print(f"ApplicationGraph > AppProc : {app_id} - val : {val} - lfc : {list_for_corrects}")
            list_for_corrects.append(val)
        else:
            print("Already in lfc!")

        event.set()
    
    def check_faulty_rsms(self):
        events = []
        list_for_corrects = []

        for elem in self.corrects:
            event_for_thr = threading.Event()
            events.append(event_for_thr)
            thr = threading.Thread(target=self.check_faulty_rsms_thread_starter, args=(elem, event_for_thr, list_for_corrects))
            thr.start()

        counter = 0
        while(counter < len(self.corrects)):
            # print(events)
            time.sleep(1.2)
            counter = 0
            for elem in events:
                if(elem.is_set()):
                    counter += 1


        print("AppGraph > list of correct rsms for each node : ", list_for_corrects)

    ################################

    ######## PFD FOR APPLICATION PROCS ########

    def check_faulty_procs_thread_starter(self, app_id, event, list_for_corrects):
        list_for_corrects.append([app_id, self.app_nodes[app_id].get_new_corrects()])
        event.set()
    
    def check_faulty_procs(self):
        events = []
        list_for_corrects = []

        for elem in self.app_nodes:
            event_for_thr = threading.Event()
            events.append(event_for_thr)
            thr = threading.Thread(target=self.check_faulty_procs_thread_starter, args=(elem, event_for_thr, list_for_corrects))
            thr.start()

        counter = 0
        while(counter < len(self.app_nodes)):
            time.sleep(0.5)
            counter = 0
            for elem in events:
                if(elem.is_set()):
                    counter += 1

        voted_nodes = {}
        for elem in self.app_nodes_list:
            voted_nodes.update({elem : 0})
            voted_nodes[0] += 1
        
        for elem in list_for_corrects:
            # id : elem[0], its corrects: elem[1]
            for detected in elem[1]:
                voted_nodes[detected] += 1
        
        threshold = min(voted_nodes.values())

        self.corrects = []
        for elem in voted_nodes:
            if(voted_nodes[elem] > threshold):
                if(elem not in self.corrects):
                    self.corrects.append(elem)

        self.corrects.sort()
        n = len(self.corrects)
        
        for elem in self.corrects:
            self.app_nodes[elem].cons.set_num_nodes(n)
        
        # print("voted_nodes: ", voted_nodes)
        print(f"ApplicationGraph > new corrects : {self.corrects}")

    ################################################

    ######## CONSENSUS FOR RSMS ########

    def get_consensus_rsms_thread_starter(self, node_id, id, msg_id, value, event):
        self.consensus_events[msg_id].append([node_id, self.app_nodes[node_id].get_rsm_consensus(id, msg_id, value)])
        event.set()

    def get_consensus_single_proc(self, id_proc, id_rsm, val):
        msg_id = str(uuid.uuid4())
        event = threading.Event()
        
        self.consensus_events[msg_id] = []
        
        thr = threading.Thread(target=self.get_consensus_rsms_thread_starter, args=(id_proc, id_rsm, msg_id, val, event))
        thr.start()
        
        while(not(event.is_set())):
            time.sleep(0.2)

        print(f"AppGraph - consensus of ensemble {id}:")
        threshold = (3 * self.byz + 1)
        if(len(self.consensus_events[msg_id][0][1][0]) < threshold):
            return False
        
        return True

    def get_consensus_rsms_processes(self, id, value):
        msg_id = str(uuid.uuid4())
        events = []
        self.consensus_events[msg_id] = []

        print(self.corrects)
        for elem in self.corrects:
            event_for_thr = threading.Event()
            events.append(event_for_thr)
            thr = threading.Thread(target=self.get_consensus_rsms_thread_starter, args=(elem, id, msg_id, value, event_for_thr))
            thr.start()
            # self.consensus_events[msg_id].append([elem, self.app_nodes[elem].get_consensus(id, msg_id, value)])
        
        counter = 0
        # time.sleep(0.5)
        print(self.corrects, len(self.corrects)) ### !
        while(counter < len(self.corrects)):
            counter = 0
            for elem in events:
                if(elem.is_set()):
                    counter += 1

        self.consensus_events[msg_id].sort()
        
        time.sleep(2.0)
        print(f"AppGraph - consensus of ensemble {id}:")
        threshold = (3 * self.byz + 1)
        for elem in self.consensus_events[msg_id]:
                print("elem[1] ", elem[1])
                n = len(elem[1][0])
                if(n < threshold):
                    print("Impossible to reach consensus, number of RSM less than (3t+1)")
                    return False
                
                print(f" - RSM {elem[0]} : {elem[1][0]}, len = {len(elem[1][0])}")

        return True

    ########################################

    def random_app_proc_choice(self):
        tmp = []
        
        for elem in self.corrects:
            tmp.append(elem)

        return random.choice(tmp)

    ######## CONSENSUS FOR APPLICATION PROCESSES ########

    def ask_consensus_app_proc_thread_starter(self, node_id, msg_id, value, event):
        self.consensus_events[msg_id].append([node_id, self.app_nodes[node_id].get_app_consensus(msg_id, value)])
        event.set()

    # asking consensus among application processes
    def ask_consensus_app_procs(self, value):
        msg_id = str(uuid.uuid4())
        self.consensus_events[msg_id] = []

        # for testing, commander is randomly chosen from corrects
        neo = self.random_app_proc_choice()
        self.app_nodes[neo].app_ask_consensus_commander(msg_id, value)
        
        tmp = []
        for elem in self.corrects:
            tmp.append(elem)

        while(len(tmp) > 0):
            for elem in tmp:
                val = self.app_nodes[elem].cons.get_val(msg_id)
                if(val != False):
                    self.consensus_events[msg_id].append(val)
                    tmp.remove(elem)

            print(tmp)
            time.sleep(0.2)

        print(f"ApplicationGraph > consensus reached : {self.consensus_events[msg_id]} among corrects : {self.corrects}")
        return self.consensus_events[msg_id]

    ################################################

    def eventGenerator(self, type, sender, recver, msg):
        if(not(sender in self.corrects) or not(recver in self.corrects)):
            print("ApplicationGraph > error while generating event!!")

        else:
            match type:
                case "SEND":
                    self.app_nodes[sender].app_proc_send_to(type, recver, msg, None, sender)
                    self.timestamp += 1
                    self.vector_clock[sender] += 1
                    self.vector_clock[recver] += 1
                    vc = self.vector_clock.copy()
                    self.happened_events.update({self.timestamp : {"type" : type, "node" : sender, "vc" : vc, "msg" : msg}})
                    print(f"ApplicationGraph > happened_events status : {self.happened_events}")
                    self.eventGenerator("RECV", sender, recver, msg)

                case "RECV":
                    self.timestamp += 1
                    self.vector_clock[sender] += 1
                    self.vector_clock[recver] += 1
                    vc = self.vector_clock.copy()
                    self.happened_events.update({self.timestamp : {"type" : type, "node" : recver, "vc" : vc, "msg" : msg}})
                    print(f"ApplicationGraph > happened_events status : {self.happened_events}")

    def app_rsm_recver(self, event_set):
        list_of_events = []

        for elem in event_set:
            list_of_events.append(EventP(event_set[elem]["type"], elem, event_set[elem]["node"], event_set[elem]["vc"], event_set[elem]["msg"]))

        for elem in self.corrects:
            self.app_nodes[elem].app_proc_rsm_input(list_of_events)

    # TODO: may need to be implemented

    ######## TESTING CAUSALITY OF EVENTS ########

    def test_causality(self, id_h, id_i, x, star):
        # checkng if x is in list of events F_h (list of events of process h)
        FOUND = False
        F_h = self.app_nodes[id_h].get_list_events()

        for elem in F_h:
            # print(f"{x} vs {elem.get_index()}")
            if(elem.get_index() == (x)): # searching for a sequence number compatible with x
                FOUND = True
                break

        if(not(FOUND)):
            return False

        # checking if star is in list of events F_i (list of events of process i)
        F_i = self.app_nodes[id_i].get_list_events()
        FOUND = False
        for elem in F_i:
            if(elem.get_index() == (star)):
                FOUND = True
                break

        if(not(FOUND)):
            return False
        
        V_tmp = self.app_nodes[id_i].V
        val = V_tmp.get_val(star, id_h)
        if(val == True):
            return True
        else:
            return (V_tmp.get_val(star, id_h) >= (x))     # !!!
    
        # star <= maxeventID(F_i)

    #############################################

    def plot_graph(self):
        pos = nx.spring_layout(self.app_graph)
        plt.title("Application Graph")
        nx.draw(self.app_graph, pos, with_labels=True, node_color='#ffc72b', node_size= 1200, edge_color='#4a4a4a')
        plt.show()

        for elem in self.app_nodes:
            self.app_nodes[elem].plot_graph()

    def cleanup(self):
        for elem in self.app_nodes:
            self.app_nodes[elem].cleanup()