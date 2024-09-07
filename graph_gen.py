import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import time
import os
import uuid
from threading import Event

# from dijkstra import Dijkstra
from graph_node import Node

# MODIFY graph_main.py FOR OBTAINING RESULTS!

# class NodeTerm:
#     def __init__(self, node):
#         self.node = node

#     def open_terminal(self):
#         neighbors = self.node.get_neighbors()
#         print(neighbors)
#         command = f'gnome-terminal -- bash -c "python3 node_term.py {self.node.id} {self.node.address} {neighbors}; exec bash"'
#         os.system(command)

class Graph:
    def __init__(self, id, num_nodes, base_port, event):
        
        self.id = str(id)
        self.nodes = {}
        
        # generates a random minimally connected graph network
        # self.G = nx.random_tree(num_nodes)
        # self.G = nx.erdos_renyi_graph(n=num_nodes, p=0.75, seed=int((time.time() / 10000) % 10000))

        self.G = nx.erdos_renyi_graph(n=num_nodes, p=0.5, seed=43)
        
        # while not nx.is_connected(self.G):
        #     (u, v) = (np.random.randint(0, num_nodes), np.random.randint(0, num_nodes))
        #     if u != v and not self.G.has_edge(u, v):
        #         self.G.add_edge(u, v)
        
        ip = "127.0.0.1" # WATCH OUT!!! Since the programm has to run locally, there is no need to use different ip than lochalhost one!
        self.base_port = base_port # first of the free usable ports for tcp stuff
        
        self.nodes_list = self.G.nodes()
        detailed_node_list = {}
        self.port_map = {}
        port_counter = base_port
        self.stop_event = event
        self.cons_events = {}
        self.consensus_events = {}
        
        # detailed_node_list -> dictionary with, for each node of the graph, the following info:
        #   <id, ip, ports: {port to neighbor, neigbor id, neighbor ip, port that neighbor uses to connect with that node}>
        # self.port_map structure -> dictionary with tuples <id of node using that port, id of node connected with>
        
        # nesteed loop cycles allowing to generate the map of the used ports for avoiding concurrency on them
        for node in self.nodes_list:
            for neighbor in self.G.neighbors(node):
                if (node, neighbor) not in self.port_map:
                    self.port_map[(node, neighbor)] = port_counter
                    self.port_map[(neighbor, node)] = port_counter + 1
                    port_counter += 2
        
        self.base_port = port_counter

        for node in self.nodes_list:
            ports_for_node = []
            for (node1, node2), port in self.port_map.items():
                if node1 == node:
                    ports_for_node.append({"port": port, "neigh": node2})

            detailed_node_list[node] = {"id": node, "ip": ip, "ports": ports_for_node}
        
        # generates, for each node, a list of info about neighbors, ports and ips
        for node in detailed_node_list:
            for elem in detailed_node_list[node]['ports']:
                neigh_id = elem['neigh']
                for neighbor in detailed_node_list[neigh_id]['ports']:
                    elem.update({"neigh_ip": ip})
                    if neighbor['neigh'] == node:
                        elem.update({"neigh_port": neighbor['port']})

        # writes onto a txt file a schematic representation of the generated network
        filename = "./txt_files/graph_" + str(uuid.uuid4()) + ".txt"
        print(f"Graph {self.id} : {str(uuid.uuid4())}")
        with open(filename, 'w') as file:
            for node in detailed_node_list:
                for port_info in detailed_node_list[node]['ports']:
                    address_1 = {detailed_node_list[node]['ip'] + ":" + str(port_info['port'])}
                    address_2 = {port_info['neigh_ip'] + ":" + str(port_info['neigh_port'])}
                    file.write(f"id: {node} - {port_info['neigh']}, addresses:  {address_1} - {address_2}\n")
        
        # generates a terminal window for each node
        for node in detailed_node_list:
            # print((detailed_node_list[node]['id'], detailed_node_list[node]['ip'], detailed_node_list[node]['ports']))
            self.nodes[node] = Node(detailed_node_list[node]['id'], detailed_node_list[node]['ip'], detailed_node_list[node]['ports'], num_nodes, None, self.stop_event)
            
            # print(f"detailed_node_list[{node}]: {detailed_node_list[node]['ports']}")
            #print("neighbors in graph_gen.py: ", self.nodes[node].get_neighbors())
        
        # if(option == 'term'):
        #     for node in self.nodes:
        #         node_term = NodeTerm(self.nodes[node])
        #         node_term.open_terminal()
        #         time.sleep(0.5)  # Slight delay to ensure terminal opens properly

    def shortPath(self, source, target):
        if(source in self.nodes_list and target in self.nodes_list) :
            path = nx.shortest_path(self.G, source = source, target = target)
            return path

    def send_msg(self, source, dest, msg):
        if(source in self.nodes_list and dest in self.nodes_list):
            # access the instance of Node for accessing "send" method ->
            # -> objects are into self.nodes!
            print(f"Node {source} > neighbors: [", end = "")
            neighs = self.nodes[source].get_neighbors()
            
            for elem in neighs:
                print(f"{elem['neigh']} ", end = "")
            print("]")
            
            FOUND = False
            for elem in neighs:
                if(dest == elem['neigh']):
                    FOUND = True
            
            if(FOUND):       
                self.nodes[source].send_to("SIMPLE", dest, str(msg + str(self.id)), self.shortPath(source, dest), None, source)
            else:
                self.nodes[source].send_to("SIMPLE", dest, str(msg + str(self.id)), [dest], None, source)


    # function for obtaining vector clock of each node, debugging purposes
    def get_matrix_clock(self):
        print(" === MATRIX CLOCK === ")
        for node in self.nodes:
            print(f"{self.nodes[node].get_id()} : \t {self.nodes[node].get_vectorClock()}")            
  
    def get_message_logs(self):
        print(" === MESSAGE LOGS === ")
        for node in self.nodes:
            print(f"{self.nodes[node].get_id()} : \t {self.nodes[node].get_msgLog()}")
  
    # plots the graph using matplotlib        
    def plot_graph(self):
        pos = nx.spring_layout(self.G)
        plt.title(f"Application process {self.id}")
        nx.draw(self.G, pos, with_labels=True, node_color='#00a4db', node_size=600, edge_color='gray')
        plt.show()
        
    # devoloping purposes function
    def first_BC_send(self):
        self.nodes[0].sendMsgBC("CIAO", str(uuid.uuid4()), 0, 0)

    def BC_send(self, node_id, msg):
        self.nodes[node_id].sendMsgBC(msg, str(uuid.uuid4()), node_id, [node_id])
        
    def specialBC(self, origin, msg):
        self.nodes[origin].specialBC_Node(msg, None)
        
    def pfd_test(self, origin):
        self.nodes[origin].pfd_caller()

    def pfd_single_result(self, node_id):
        if(node_id in self.nodes):
            return self.nodes[node_id].pfd_caller()
        
    def set_same_input_rsm(self, event_set):
        for node in self.nodes:
            self.nodes[node].set_RSM_input_set(event_set)

    def get_port_counter(self):
        return self.base_port

    def ask_consensus(self, id, msg_id, msg):
        self.consensus_events[msg_id] = []

        if(id in self.nodes):
            self.nodes[id].asking_for_consensus_commander(msg_id, msg)
        
        while(len(self.consensus_events[msg_id]) < len(self.nodes)):
            # self.print_agreed_values()
            for elem in self.nodes:
                FOUND = False

                for e in self.consensus_events[msg_id]:
                    if(elem in e):
                        FOUND = True
                        break
                     
                if(not FOUND):
                    v = self.nodes[elem].is_chosen(msg_id) 

                    if(v != False):
                        self.consensus_events[msg_id].append({elem : v})

        print(f"Graph {self.id} > consensus reached : {self.consensus_events[msg_id]}")
        return self.consensus_events[msg_id]
        
    def print_agreed_values(self):
        for node in self.nodes:
            print(f"Node {node} § ", end = "")
            self.nodes[node].get_values()
            print(f"{self.nodes[node].cons.values}\n")
            
            # while(self.nodes[node].get_cons_status() == False):
            #     pass
            
            # print(f"Node {self.nodes[node].get_id()} : {self.nodes[node].get_value()}")

    def setup_consensus_event(self, msg_id):
        if(msg_id not in self.cons_events):
            self.cons_events.update[msg_id] = {}

    def get_size(self):
        return len(self.nodes)

    def cleanup(self):
        for node in self.nodes:
            self.nodes[node].cleanup()