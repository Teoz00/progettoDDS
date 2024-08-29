from app_process import ApplicationProcess
from pp2p import PerfectPointToPointLink
from threading import Event

import networkx as nx
import matplotlib.pyplot as plt

###

class ApplicationGraph:
    def __init__(self, num_apps, t_byzantine):
        
        self.app_graph = self.G = nx.erdos_renyi_graph(n=num_apps, p=0.75, seed=43)
        self.stop_event = Event()
        
        ip = "127.0.0.1"
        base_port = 49152
        port_counter = base_port

        self.app_nodes = {}
        self.app_nodes_list = self.app_graph.nodes()
        self.port_map = {}
        detailed_app_nodes_list = {}

        self.stop_event = Event()

        for node in self.app_nodes_list:
            for neighbor in self.app_graph.neighbors(node):
                if (node, neighbor) not in self.port_map:
                    self.port_map[(node, neighbor)] = port_counter
                    self.port_map[(neighbor, node)] = port_counter + 1
                    port_counter += 2

        for node in self.app_nodes_list:
            print(node)
            ports_for_node = []
            for (node1, node2), port in self.port_map.items():
                if node1 == node:
                    ports_for_node.append({"port": port, "neigh": node2})
              
            detailed_app_nodes_list[node] = {"id": node, "ip": ip, "ports": ports_for_node}
        
        nodes_per_subgraph = int(3 * int(t_byzantine) + 1)

        for node in detailed_app_nodes_list:
            self.app_nodes[node] = ApplicationProcess(detailed_app_nodes_list[node]['id'], detailed_app_nodes_list[node]['ip'], detailed_app_nodes_list[node]['ports'], nodes_per_subgraph, port_counter, self.stop_event)
            port_counter = self.app_nodes[node].get_port_counter()
            

    def plot_graph(self):
        pos = nx.spring_layout(self.G)
        plt.title("Application Graph")
        nx.draw(self.G, pos, with_labels=True, node_color='#ffc72b', node_size=800, edge_color='#4a4a4a')
        plt.show()

        for elem in self.app_nodes:
            self.app_nodes[elem].plot_graph()

    def cleanup(self):
        for elem in self.app_nodes:
            self.app_nodes[elem].cleanup()
