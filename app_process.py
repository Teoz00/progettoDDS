from graph_gen import Graph

class ApplicationProcess:
    def __init__(self, my_id, my_addr, neighbors, number_node, base_port, stop_event, cons_event):

        self.id = my_id
        self.subgraph = Graph(my_id, number_node, base_port, stop_event)
        self.consensus = []
        # self.subgraph.set_same_input_rsm(None)

        # my_id, my_addr, neighbors to be used for communication between ApplicacionProcesses

    def get_port_counter(self):
        return self.subgraph.get_port_counter()
    
    def get_consensus(self, id, msg):
        cons = []
        if(id in self.subgraph.nodes):
            self.subgraph.nodes[id].asking_for_consensus_commander(msg)
            cons.append([id, self.subgraph.nodes[id].get_values()])
        
        print(f"ApplicationProcess {self.id}> consensus list {cons}")

    def plot_graph(self):
        self.subgraph.plot_graph()

    def cleanup(self):
        self.subgraph.cleanup()