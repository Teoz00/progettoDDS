from app_process import ApplicationProcess
from pp2p import PerfectPointToPointLink

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

        # consensus for each message has an entry into a dedicated structure
        self.consensus_events = {}

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
        
        nodes_per_subgraph = int(3 * int(t_byzantine) + 1)

        # self.consensus_events[detailed_app_nodes_list[node]['id']]

        for node in detailed_app_nodes_list:
            for elem in detailed_app_nodes_list[node]['ports']:
                neigh_id = elem['neigh']
                for neighbor in detailed_app_nodes_list[neigh_id]['ports']:
                    elem.update({"neigh_ip": ip})
                    if neighbor['neigh'] == node:
                        elem.update({"neigh_port": neighbor['port']})

            self.app_nodes[node] = ApplicationProcess(detailed_app_nodes_list[node]['id'], detailed_app_nodes_list[node]['ip'], detailed_app_nodes_list[node]['ports'], nodes_per_subgraph, num_apps, port_counter, self.stop_event)
            port_counter = self.app_nodes[node].get_port_counter()

    ######## PFD FOR RSMS #######

    def check_faulty_rsms_thread_starter(self, app_id, node_id, event, list_for_corrects):
        list_for_corrects.append([node_id, self.app_nodes[app_id].check_faulty_rsms(node_id)])
        event.set()
    
    def check_faulty_rsms(self):
        events = []
        list_for_corrects = []

        for elem in self.app_nodes:
            event_for_thr = threading.Event()
            events.append(event_for_thr)
            thr = threading.Thread(target=self.check_faulty_rsms_thread_starter, args=(elem, random.randint(0, self.app_nodes[elem].get_num_nodes()-1), event_for_thr, list_for_corrects))
            thr.start()

        counter = 0
        while(counter < len(self.app_nodes)):
            # time.sleep(2.5)
            counter = 0
            for elem in events:
                if(elem.is_set()):
                    counter += 1

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
        print(f"ApplicationGraph > new corrects : {self.corrects}")

    ################################################

    ######## CONSENSUS FOR RSMS ########

    def get_consensus_rsms_thread_starter(self, node_id, id, msg_id, value, event):
        self.consensus_events[msg_id].append([node_id, self.app_nodes[node_id].get_rsm_consensus(id, msg_id, value)])
        event.set()

    def get_consensus_rsms_processes(self, id, value):
        msg_id = str(uuid.uuid4())
        events = []
        self.consensus_events[msg_id] = []

        for elem in self.corrects:
            event_for_thr = threading.Event()
            events.append(event_for_thr)
            thr = threading.Thread(target=self.get_consensus_rsms_thread_starter, args=(elem, id, msg_id, value, event_for_thr))
            thr.start()
            # self.consensus_events[msg_id].append([elem, self.app_nodes[elem].get_consensus(id, msg_id, value)])
        
        counter = 0
        while(counter < len(self.corrects)):
            # time.sleep(2.5)
            counter = 0
            for elem in events:
                if(elem.is_set()):
                    counter += 1

        self.consensus_events[msg_id].sort()
        
        # time.sleep(2.0)
        print(f"AppGraph - consensus :\n", end = "")
        for elem in self.consensus_events[msg_id]:
                print("\t", elem)

    ########################################

    def random_app_proc_choice(self):
        tmp = []
        
        for elem in self.app_nodes_list:
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
        
        while(len(self.consensus_events[msg_id]) < len(self.app_nodes)):
            for elem in self.app_nodes:
                FOUND = False

                for e in self.consensus_events[msg_id]:
                    if(elem in e):
                        FOUND = True
                        break
                    
                if(not FOUND):
                    v = self.app_nodes[elem].is_chosen(msg_id) 

                    if(v != False):
                        self.consensus_events[msg_id].append({elem : v})
                
                time.sleep(0.1)

        print(f"ApplicationGraph > consensus reached : {self.consensus_events[msg_id]}")
        return self.consensus_events[msg_id]

    ################################################

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