from graph_gen import Graph

class ApplicationProcess:
    def __init__(self, my_id, my_addr, neighbors, number_node, base_port, event):

        self.subgraph = Graph(my_id, number_node, base_port, event)
        # self.subgraph.set_same_input_rsm(None)

        # my_id, my_addr, neighbors to be used for communication between ApplicacionProcesses

    def get_port_counter(self):
        return self.subgraph.get_port_counter()
    
    def plot_graph(self):
        self.subgraph.plot_graph()

    def cleanup(self):
        self.subgraph.cleanup()