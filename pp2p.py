# ZeroMQ will be used for networking events and message exchange
import zmq
class PerfectPointToPointLink:
    def __init__(self, my_addr, peer_addr):
        # initial stuff
        self.address = my_addr
        self.peer_addr = peer_addr
        
        # generation of context and connections
        self.context = zmq.Context()

        reconnections = 5
        attempts = 0

        # recv socket init
        try:
            self.recv_socket = self.context.socket(zmq.PULL)
            self.recv_socket.bind(f"tcp://{self.address}")
            
        except Exception as e:        
            print(f"Link {self.address} : catched '{e}' while binding with {self.peer_addr}")
            if(attempts < reconnections):
                try:
                    self.recv_socket = self.context.socket(zmq.PULL)
                    self.recv_socket.bind(f"tcp://{self.address}")
                except:
                    print(f"Link {self.address}: attempt {attempts + 1} failed")

        # send socket init
        try:
            self.send_socket = self.context.socket(zmq.PUSH)
            self.send_socket.connect(f"tcp://{self.peer_addr}")
        except Exception as e:
            print(f"Link {self.address}: catched '{e}' while connecting to {self.peer_addr}")


    def print_info(self):
        print("PP2P info: ", self.address, " - ", self.peer_addr)
      
    def get_peer_addr(self):
        return self.peer_addr
        
    # simply send information through the socket to the specified destination
    def send(self, msg):
        # print(f"i'm sending {msg}")
        self.send_socket.send_string(str(msg))
    
    # handles receive operation
    def recv(self):
        try:
            msg = self.recv_socket.recv_string(zmq.NOBLOCK)
            # print("Received: ", msg)
            return msg
        except zmq.Again:
            return None
        
    def close(self):
        try:
            self.recv_socket.close()
        except Exception as e:
            print(f"Link {self.address}: catched '{e}' while closing recv socket")
        
        try:
            self.send_socket.close()
        except Exception as e:
            print(f"Link {self.address}: catched '{e}' while closing send socket")
        
        try:
            self.context.term()
        except Exception as e:
            print(f"Link {self.address}: catched '{e}' while terminating context")