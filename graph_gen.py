import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import time
import os
import uuid

# from dijkstra import Dijkstra
from graph_node import Node

# MODIFY graph_main.py FOR OBTAINING RESULTS!

class NodeTerm:
    def __init__(self, node):
        self.node = node

    def open_terminal(self):
        neighbors = self.node.get_neighbors()
        print(neighbors)
        command = f'gnome-terminal -- bash -c "python3 node_term.py {self.node.id} {self.node.address} {neighbors}; exec bash"'
        os.system(command)

class Graph:
    def __init__(self, num_nodes, option):
        self.nodes = {}
        
        # generates a random minimally connected graph network
        self.G = nx.random_tree(num_nodes)
        
        while not nx.is_connected(self.G):
            (u, v) = (np.random.randint(0, num_nodes), np.random.randint(0, num_nodes))
            if u != v and not self.G.has_edge(u, v):
                self.G.add_edge(u, v)
        
        ip = "127.0.0.1" # WATCH OUT!!! Since the programm has to run locally, there is no need to use different ip than lochalhost one!
        base_port = 49152 # first of the free usable ports for tcp stuff
        
        self.nodes_list = self.G.nodes()
        detailed_node_list = {}
        self.port_map = {}
        port_counter = base_port
        
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
        filename = "graph.txt"
        with open(filename, 'w') as file:
            for node in detailed_node_list:
                for port_info in detailed_node_list[node]['ports']:
                    address_1 = {detailed_node_list[node]['ip'] + ":" + str(port_info['port'])}
                    address_2 = {port_info['neigh_ip'] + ":" + str(port_info['neigh_port'])}
                    file.write(f"id: {node} - {port_info['neigh']}, addresses:  {address_1} - {address_2}\n")
        
        # generates a terminal window for each node
        for node in detailed_node_list:
            # print((detailed_node_list[node]['id'], detailed_node_list[node]['ip'], detailed_node_list[node]['ports']))
            self.nodes[node] = Node(detailed_node_list[node]['id'], detailed_node_list[node]['ip'], detailed_node_list[node]['ports'], num_nodes)
            
            # print(f"detailed_node_list[{node}]: {detailed_node_list[node]['ports']}")
            #print("neighbors in graph_gen.py: ", self.nodes[node].get_neighbors())
        
        if(option == 'term'):
            for node in self.nodes:
                node_term = NodeTerm(self.nodes[node])
                node_term.open_terminal()
                time.sleep(0.5)  # Slight delay to ensure terminal opens properly

    def shortPath(self, source, target):
        if(source in self.nodes_list and target in self.nodes_list) :
            path = nx.shortest_path(self.G, source = source, target = target)
            return path

    def send_msg(self, source, dest, msg):
        if(source in self.nodes_list and dest in self.nodes_list):
            # access the instance of Node for accessing "send" method ->
            # -> objects are into self.nodes!
            self.nodes[source].send_to("SIMPLE", dest, msg, self.shortPath(source, dest), None, source)

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
        nx.draw(self.G, pos, with_labels=True, node_color='skyblue', node_size=800, edge_color='gray')
        plt.title("Connect Undirected graph")
        plt.show()
        
    # devoloping purposes function
    def first_BC_send(self):
        self.nodes[0].sendMsgBC("CIAO", str(uuid.uuid4()), 0, 0)

    def BC_send(self, node_id, msg):
        self.nodes[node_id].sendMsgBC(msg, str(uuid.uuid4()), node_id, [node_id])
        
    def specialBC(self, origin, msg):
        self.nodes[origin].specialBC_Node(msg)
