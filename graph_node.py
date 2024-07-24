from pp2p import PerfectPointToPointLink

class Node:
    def __init__(self, my_id, my_addr, neighbors):
        self.id = my_id
        self.links = {}
        self.messageLog = []
        
        # TODO
        # start
        n = len(neighbors)
        self.vectorClock = [0] * (n + 1)
        # end
        
        for elem in neighbors:
            # print(my_addr + ":" + str(elem['port']), my_addr)
            self.links.update({str(elem['neigh']): PerfectPointToPointLink(my_addr + ":" + str(elem['port']), str(elem['neigh_ip']) + ":" + str(elem['neigh_port']))})

    def send_to(self, peer_id, msg):
        try:
            if not(isinstance(peer_id, str)):
                peer_id = str(peer_id)
                
            self.links[peer_id].send(msg)
        except:
            print("Impossible to send a message to specified peer")
            
    def recv_from(self):
        for link in self.links:
            link.recv()