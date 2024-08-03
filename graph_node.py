import threading
import traceback
import time
import ast
import os
import signal
import uuid

from pp2p import PerfectPointToPointLink
from event_process import EventP

class Node:
    def __init__(self, my_id, my_addr, neighbors, all):
        self.id = my_id
        self.links = {}
        self.address = my_addr
        self.node_into_network = int(all)
        self.event_set = []
        
        self.vectorClock = [0] * (self.node_into_network)
        self.messageLog = []
        
        self.neighbors = neighbors
        
        self.listener_threads = {}
        self.stop_event = threading.Event()
        
        self.acks_received = {}
        self.pending_acks = {}
        self.ack_timeout = 10  # seconds to wait for an ack
        self.ack_flags = {}  # to store ack status (True/False) of each message sent
        self.message_sent_flags = {}  # to store sent status of each message
        # print(f"neighbors into {self.id} : {neighbors}")
        # print(self.id, " -> ", neighbors)
        self.ackBC = {}
        
        for elem in neighbors:
            # print(my_addr + ":" + str(elem['port']), my_addr)
            link_addr = f"{my_addr}:{elem['port']}"
            neigh_addr = f"{elem['neigh_ip']}:{elem['neigh_port']}"
            self.links.update({str(elem['neigh']): PerfectPointToPointLink(link_addr, neigh_addr)})
            # print("LINK!!! ", self.links[str(elem['neigh'])])
             
            try:
                self.running = True
                # print(f"scanning {self.id}:{elem['neigh_port']}")
                thr = threading.Thread(target=self.listen_msg, args=(self.links[str(elem['neigh'])],))
                self.listener_threads.update({elem['neigh']: thr})
                # print(f"{self.id} -> {self.listener_threads[elem['neigh']]}")
                self.listener_threads[elem['neigh']].start()
            
            except Exception as e:
                print(f"Catched: {e} while starting thread at {self.id}:{elem['neigh_port']}")
                # self.cleanup()

                 
    def manage_vector_clock(self, vc):
        if(not(isinstance(vc, list))):
            vc = ast.literal_eval(vc)

        for i in range(0, self.node_into_network):
            if(self.vectorClock[i] < vc[i]):
                self.vectorClock[i] = vc[i]
        
    def send_to(self, peer_id, msg, shortestPath, message_id=None):
        try:
            if not(isinstance(peer_id, str)):      
                FOUND = False
                for elem in self.neighbors:
                    # print(f'{self.id}: {peer_id} vs {elem["neigh"]} -> {elem["neigh"] == peer_id}')
                    # print("debugging: ", self.links[str(elem['neigh'])])
                    # print("link: ", self.links.keys(elem["neigh"]))
                    
                    if elem["neigh"] == peer_id:
                        # print(f"{self.id} - {elem["neigh"]}")
                        # print("does exist? ", self.links[str(peer_id)]
                        self.vectorClock[self.id] += 1
                        
                        if message_id is None:
                            message_id = str(uuid.uuid4())  # Unique message ID
                        
                        self.links[str(peer_id)].send([msg, shortestPath, self.vectorClock, message_id])
                        
                        FOUND = True
                        typeOf = "send"
                        self.eventGenerating(msg, typeOf)
                        
                        self.pending_acks[message_id] = (msg, shortestPath, peer_id, time.time())
                        self.ack_flags[message_id] = False  # Initialize ack flag to False
                        self.message_sent_flags[message_id] = True  # Mark message as sent
                        
                        #print(f"Node {self.id} sent message {msg} with ID {message_id} to {peer_id}")
                        #self.event_set[len(self.event_set) - 1]
                        break
                
                if FOUND == False:
                    idx = shortestPath.index(self.id) + 1
                    # print("idx:", idx)
                    
                    if(idx < len(shortestPath)):
                        next_hop = shortestPath[idx]
                        for elem in self.neighbors:
                            # print(f'{self.id}: [searching NEAREST NEIGHBOR] {shortestPath[idx]} vs {elem["neigh"]} -> {elem["neigh"] == shortestPath[idx]}')
                
                            # DIFFERENT WAY TO MOVE INTO 'shortestPath' variable:
                            #   using the method 'index[x]' it can be possible to find
                            #   the index of object 'x' into it, so, this can be useful for avoiding
                            #   element deletion from that variable (can be reused for ack of reception!!!)
                            
                            if elem["neigh"] == next_hop: 
                                self.vectorClock[self.id] += 1
                                
                                if message_id is None:
                                    message_id = str(uuid.uuid4())  # Unique message ID
                                
                                self.links[str(elem['neigh'])].send(str([msg, shortestPath, self.vectorClock, message_id]))
                                
                                typeOf = "send"
                                self.eventGenerating(msg, typeOf)
                                
                                self.pending_acks[message_id] = (msg, shortestPath, elem['neigh'], time.time())
                                self.ack_flags[message_id] = False  # Initialize ack flag to False
                                self.message_sent_flags[message_id] = True  # Mark message as sent
                                #print(f"Node {self.id} forwarded message {msg} with ID {message_id} to {elem['neigh']}")
                                break
                    
                    # OLD IMPLEMENTATION
                    # for elem in self.neighbors:
                    #     print(f'{self.id}: [searching NEAREST NEIGHBOR] {shortestPath[]} vs {elem["neigh"]} -> {elem["neigh"] == shortestPath[0]}')
                    #     if elem["neigh"] == shortestPath[0]: 
                    #         shortestPath.pop(0)
                    #         self.links[str(elem['neigh'])].send(str([msg, shortestPath]))
                
        except Exception as e:
            print(f"\tRaised: {e}")
            # print(f"Stacktrace::: {traceback.print_exc()}")
            # print(f"Impossible to send a message to specified peer - {e}")
    
    def spawn_terminal(self):
        self.running = True
        self.listener_thread = threading.Thread(target=self.listen_msg)
        self.listener_thread.start()
        
        self.input_thread = threading.Thread(target=self.handle_input)
        self.input_thread.start()

    # when is received a payload from a node, it reconstructs the internal element of the message
    def reconstruct_payload(s):
        parsed_message = ast.literal_eval(s)

        msg = parsed_message[0]
        shortPath = parsed_message[1]

        print(f"msg: {msg}")
        print(f"shortPath: {shortPath}")

    # for each of the link, it listens for possible incoming messages
    def listen_msg(self, link):
       # try:
            # context = zmq.Context()
            # receiver = context.socket(zmq.PULL)
            # receiver.bind(f"tcp://{self.address}:{port}")
            # print(f"starting listening at {self.address}:{port} ...")
            
            while not(self.stop_event.is_set()):
                message = link.recv()
                
                if message is not None:
                    self.messageLog.append(message)
                    
                    if message.startswith("ack:"):
                        message_id = message.split(":")[1]
                
                        #Find the sending node
                        sender_id = self.get_node_id_by_link(link)
                        print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Node {self.id} received ack for message ID {message_id} from {sender_id}")
                        
                        self.manage_vector_clock(message.split(":")[2])
                        self.vectorClock[self.id] += 1
                        
                        self.handle_received_ack(message_id)
                    else:
                        reconstructed_payload = ast.literal_eval(message)
                        
                        msg = reconstructed_payload[0]
                        shortPath = reconstructed_payload[1]
                        vc = reconstructed_payload[2]
                        message_id = reconstructed_payload[3]

                        self.manage_vector_clock(vc)
                        self.vectorClock[self.id] += 1                        
                        
                        typeOf = "receive"
                        self.eventGenerating(msg, typeOf)
                        
                        if self.id == shortPath[-1]:
                            print(f"Node {self.id} received {msg} from {shortPath[0]}")
                            self.vectorClock[self.id] += 1
                            self.send_ack(link, message_id)
                            self.stop_event.set()  # send event for stopping threads
                            
                        else:
                            shortPathLen = len(shortPath)
                            self.vectorClock[self.id] += 1

                            if shortPathLen == 1 :
                               # print(f"ShortPath: {shortPath[0]}\n")
                                if shortPath[0] != self.id:
                                    self.ackBC[message_id] = {"msg":msg, "shortPath":shortPath, "neighbor": link.get_peer_addr(), "time":time.time(), "counter": 0}
                                    threading.Thread(target = self.handleAckBC , args = (message_id , link))

                                    for neigh in self.neighbors:
                                        #print(f"neigh['neigh_ip']: {neigh['neigh_port']}\n")
                                       # print(f"\tlink_peer_addr{type(link.get_peer_addr())}\tnigh_ip:{type(neigh['neigh']['neigh_ip'])}\tport:{type(neigh['neigh']['neigh_port'])}\n")
                                        
                                        if neigh["neigh"] != shortPath[0] and link.get_peer_addr() != neigh["neigh_ip"]+str(neigh["neigh_port"]):     
                                            self.ack_flags[message_id] = False  # Initialize ack flag to False
                                            self.message_sent_flags[message_id] = True  # Mark message as sent            
                                            self.send_to(neigh["neigh"], "ack:"+msg, shortPath, message_id)
                                            
                                print(f"ACK for BC -->\t{time.strftime('%Y-%m-%d %H:%M:%S')} - Node {self.id} forwarding {message} to {link.get_peer_addr()}")

                            else:
                                next_hop = shortPath[shortPath.index(self.id) + 1]                            
                                print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Node {self.id} forwarding {message} to {next_hop}")
                                self.send_to(next_hop, msg, shortPath, message_id)  # Use the same message ID
                             
                            typeOf = "send"
                            self.eventGenerating(msg, typeOf)
                            
                time.sleep(0.5)
                
      #  except Exception as e:
        #    print(f"Catched: {e} while trying to listen at {self.id}:{link}")
            # print(f"Stacktrace::: {traceback.print_exc()}")
        #finally:
         #   self.cleanup()
    
    def get_id(self):
        return self.id
    
    def get_vectorClock(self):
        return self.vectorClock
    
    def get_msgLog(self):
        return self.messageLog
    
    def get_node_id_by_link(self, link):
        for node_id, node_link in self.links.items():
            if node_link == link:
                return node_id
        return "unknown" # If link not found, return default value
     
    def handle_input(self):
        while self.running:
            command = input(f"Node {self.id} > ")
            if command.startswith("send"):
                _, target_id, message = command.split(maxsplit=2)
                target_id = int(target_id)
                self.send_to(target_id, message, shortestPath=[self.id, target_id])  # Provide shortestPath
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

    def cleanup(self):
        self.stop_event.set()
        # Set running to False to stop all threads
        self.running = False
        # Join all listener threads to ensure they have finished
        # for thr in self.listener_threads.values():
        #   thr.join() # not useful anymore due to stop event globally notified to each thread
        # Close all links to release resources
        for link in self.links.values():
            link.close()

    def eventGenerating(self, msg, type):
        self.event_set.append(EventP(type, len(self.event_set), self.vectorClock, msg))
        #print(f"EventSet{self.id}:{self.event_set}")
    
    #function that sends an ack message
    def send_ack(self, link, message_id):
        ack_message = f"ack:{message_id}:{self.vectorClock}"
        link.send(ack_message)
    
    #function that periodically checks for pending ACKs
    def check_pending_acks(self):
        current_time = time.time()
        for message_id, (msg, shortestPath, peer_id, timestamp) in list(self.pending_acks.items()):
            if current_time - timestamp > self.ack_timeout:
                (f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Resending message {msg} to {peer_id}")
                self.send_to(peer_id, msg, shortestPath, message_id)
                self.pending_acks[message_id] = (msg, shortestPath, peer_id, current_time)
    
    #function that runs a continuous loop to check for pending ACKs
    def check_pending_acks_loop(self):
        while self.running:
            self.check_pending_acks()
            time.sleep(1)
    
    #Start the thread that runs check_pending_acks_loop:
    def start_ack_checker(self):
        self.ack_checker_thread = threading.Thread(target=self.check_pending_acks_loop)
        self.ack_checker_thread.start()
    
    #function that manages received acks
    def handle_received_ack(self, message_id):
    # Check if the ack is for a pending message
        if message_id in self.pending_acks:            
            (msg, shortestPath, peer_id, timestamp) = self.pending_acks[message_id]
        
            # Find the index of the current node in the path
            if len(shortestPath) > 1:
                index = shortestPath.index(self.id)
            
                # If the current node is not the first in the path
                if index > 0:
                    # The previous node is the leftmost node in the path
                    next_hop = shortestPath[index - 1]
                
                    # Send ack to previous node
                    self.send_ack(self.links[str(next_hop)], message_id)
                    print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Node {self.id} sending ack for message ID {message_id} to {next_hop}")
                    #print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Node {self.id} received ack from {peer_id} and sending ack to {next_hop} for message ID {message_id}")
           
        
    def handleAckBC(self, message_id, link): #NB message_id is a string or int 
        #TODO timeout implementation for ack waiting assigned to other threads
        while self.ackBC[message_id]["counter"] < len(self.neighbors):
            time.sleep(0.5)
        
        self.send_ack(link , message_id)  

    def broadcast(self, msg):
        #"""Broadcasts a message to all neighbors."""
        self.vectorClock[self.id] += 1
        shortestPath = [self.id]  # Start the path with the current node's ID -- good for ACK
        for neighbor in self.neighbors:
            try:
                if(neighbor["neigh"] != self.id):
                    self.send_to(neighbor["neigh"], msg, shortestPath)
                    print(f"{self.id} : ShortestPath --> {shortestPath} / {neighbor}")
            except Exception as e:
                print(f"Failed to send to neighbor {neighbor['neigh']}: {e}")