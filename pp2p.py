import zmq

class PerfectPointToPointLink:
    def __init__(self, first_node, second_node, my_addr, peer_addr):
        # initial stuff
        self.id = "first_node" + "second_node"
        self.address = my_addr
        self.peer_addr = peer_addr
        
        # generation of context and connections
        self.context = zmq.Context()

        # recv socket init
        self.recv_socket = self.context.socket(zmq.PULL)
        self.recv_socket.bind(f"tcp://{self.address}")

        # send socket init
        self.send_socket = self.context.socket(zmq.PUSH)
        self.send_socket.connect(f"tcp://{self.peer_addr}")

    def print_info(self):
        print("PP2P info: ", self.id, " - ", self.address, " - ", self.peer_addr)
        
    def send(self, msg):
        self.send_socket.send_string(msg)
    
    # handles receive operation
    def recv(self):
        try:
            msg = self.recv_socket.recv_string(zmq.NOBLOCK)
            print("Received: ", msg)
            return msg
        except zmq.Again:
            return None
    