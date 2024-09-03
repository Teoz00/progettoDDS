from graph_gen import Graph

class ApplicationProcess:
    def __init__(self, my_id, my_addr, neighbors, number_node, base_port, stop_event):

        self.id = my_id
        self.subgraph = Graph(my_id, number_node, base_port, stop_event)
        self.consensus = []
        # self.subgraph.set_same_input_rsm(None)

        # my_id, my_addr, neighbors to be used for communication between ApplicacionProcesses

    def get_port_counter(self):
        pc = self.subgraph.get_port_counter()
        return pc
    
    def get_consensus(self, id, msg_id, msg):
        cons = []
        if(id in self.subgraph.nodes):
            cons.append(self.subgraph.ask_consensus(id, msg_id, msg))
            # self.subgraph.nodes[id].asking_for_consensus_commander(msg)
        
        # print(f"ApplicationProcess {self.id} > consensus list {cons}")
        return cons

    def print_cons(self):
        # print("print_cons invoked")
        self.subgraph.print_agreed_values()

    def plot_graph(self):
        self.subgraph.plot_graph()

    def cleanup(self):
        self.subgraph.cleanup()