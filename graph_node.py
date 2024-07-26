import threading
import zmq

from pp2p import PerfectPointToPointLink

class Node:
    def __init__(self, my_id, my_addr, neighbors):
        self.id = my_id
        self.links = {}
        self.address = my_addr
        self.messageLog = []
        self.neighbors = neighbors
        
        n = len(neighbors)
        self.vectorClock = [0] * (n + 1)
        
        # print(f"neighbors into {self.id} : {neighbors}")
        
        for elem in neighbors:
            print("into graph_node ", elem['neigh'])
            # print(my_addr + ":" + str(elem['port']), my_addr)
            self.links.update({str(elem['neigh']): PerfectPointToPointLink(my_addr + ":" + str(elem['port']), str(elem['neigh_ip']) + ":" + str(elem['neigh_port']))})
            
    def send_to(self, peer_id, msg, shortestPath):
        try:
            if not(isinstance(peer_id, str)):
                FOUND = False
                for elem in self.neighbors:
                    if elem["neigh"] == peer_id:
                        peer_id = str(peer_id)
                        self.links.keys(peer_id).send([msg, shortestPath])
                        FOUND = True
                        break 
                
                if not FOUND:
                    for elem in self.neighbors:
                        if elem["neigh"] == shortestPath[0]: 
                            shortestPath.pop(0)
                            self.links.keys(elem["neigh"]).send([msg, shortestPath])
                
            self.links[peer_id].send(msg)

        except:
            print("Impossible to send a message to specified peer")
            
    def recv_from(self):
        for link in self.links:
            packet = link.recv()
            source = link["neigh"] 
            shortestPath = self.links.keys().send()
            peer_id = shortestPath[0]

    def spawn_terminal(self):
        self.running = True
        self.listener_thread = threading.Thread(target=self.listen_msg)
        self.listener_thread.start()
        
        self.input_thread = threading.Thread(target=self.handle_input)
        self.input_thread.start()

    def listen_msg(self):
        context = zmq.Context()
        receiver = context.socket(zmq.PULL)
        receiver.bind(f"tcp://{self.address}")

        while self.running:
            message = receiver.recv_string()
            print(f"Node {self.id} received message: {message}")

    def handle_input(self):
        while self.running:
            command = input(f"Node {self.id} > ")
            if command.startswith("send"):
                _, target_id, message = command.split(maxsplit=2)
                target_id = int(target_id)
                self.send_to(target_id, message)
            elif command == "exit":
                self.running = False
            else:
                print("Invalid command")
                
    def get_neighbors(self):
        # list_neighbors = []
        # print(f"sizeof(links): {len(self.links)}")
        
        # for elem in self.links:
        #     list_neighbors.append(elem)
        #     print(self.links[elem]['port'])
        # print(f"list_neighbors: {list_neighbors}")
        
        return self.neighbors
