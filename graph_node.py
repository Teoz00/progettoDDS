import threading
import time
import ast
import uuid

from pp2p import PerfectPointToPointLink
from event_process import EventP
from pfd import PerfectFailureDetector

class Node:
    def __init__(self, my_id, my_addr, neighbors, all, delay, event):
        self.id = my_id
        
        # it contains all pp2p links needed for communicating with neighbors, dictionary
        self.links = {}
        self.address = my_addr
        self.node_into_network = int(all)
        
        self.corrects = []
        
        # list of events happened during the execution
        self.event_set = []
        
        self.vectorClock = [0] * (self.node_into_network)
        
        # list of messages received during the execution
        self.messageLog = []
        
        # list of dictionaries
        self.neighbors = neighbors
        
        # dictionary containing all threads used for listening messages
        self.listener_threads = {}
        self.stop_event = event
                
        self.acks_received = {}
        self.pending_acks = {"ACK":{}}
        self.pending_fwd_acks = {}
        
        self.fwd_senders = {}
        
        self.ack_timeout = 10  # seconds to wait for an ack
        self.ack_flags = {}  # to store ack status (True/False) of each message sent
        self.message_sent_flags = {}  # to store sent status of each message
        # print(f"neighbors into {self.id} : {neighbors}")
        # print(self.id, " -> ", neighbors)
        
        self.sent_to = {}
        self.received_with_id = {}
                
        self.delay = 0
        
        self.pfd = PerfectFailureDetector()
        
        if(delay == None):
            self.delay = 0.5
        else:
            self.delay = delay
        
        if(self.id == 5):
            self.delay = 3.0
        
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
                
        for i in range(0, self.node_into_network):
            if(i != self.id):
                self.corrects.append(i)

                 
    def manage_vector_clock(self, vc):
        if(not(isinstance(vc, list))):
            vc = ast.literal_eval(vc)

        for i in range(0, self.node_into_network):
            if(self.vectorClock[i] < vc[i]):
                self.vectorClock[i] = vc[i]
    
    def send_to(self, type, peer_id, msg, shortestPath, message_id, origin):
        # try:
            print(f"Node {self.id} > sending [{type, peer_id, msg, shortestPath, message_id, origin}] to {peer_id}")
            
            if message_id is None:
                message_id = str(uuid.uuid4())  # Unique message ID
                        
            self.messageLog.append((type, peer_id, msg, shortestPath, message_id, origin))
            if not(isinstance(peer_id, str)):      
                FOUND = False
                
                if(message_id not in self.sent_to):
                    self.sent_to[message_id] = {}
                
                for elem in self.neighbors:
                    # print(f'{self.id}: {peer_id} vs {elem["neigh"]} -> {elem["neigh"] == peer_id}')
                    # print("debugging: ", self.links[str(elem['neigh'])])
                    # print("link: ", self.links.keys(elem["neigh"]))
                    
                    if elem["neigh"] == peer_id:
                        # print(f"{self.id} - {elem["neigh"]}")
                        # print("does exist? ", self.links[str(peer_id)]
                        
                        if(peer_id in self.sent_to[message_id]):
                            if ([shortestPath, origin] in self.sent_to[message_id][peer_id]):
                                print(f"Node {self.id} > {message_id} previously sent to {peer_id}, aborting send...\n")
                                FOUND = True
                                break
                        else:
                            self.sent_to[message_id][peer_id] = []
                            
                        self.vectorClock[self.id] += 1
                              
                        match type:
                            
                            case "ACK":
                                if(len(shortestPath) == 1):
                                    self.links[str(peer_id)].send([type, msg, shortestPath, self.vectorClock, message_id, origin])
                                else:
                                    self.links[str(peer_id)].send([type, msg, shortestPath, self.vectorClock, message_id])                                                                
                                #self.pending_acks[type].update({message_id:0})
                                
                            case "ACK_BC":
                                # print(f"send {type, msg, shortestPath, self.vectorClock, message_id} to {peer_id}")
                                # print("message_id riga 92: ", message_id)
                                #print("pending_fwd_acks: ", self.pending_fwd_acks[message_id])
                                # for elem in self.pending_fwd_acks[str(message_id)]:
                                #     print(f"Node {self.id} - {elem} > sending ACK_BC...")
                                #     if(elem["node"] == peer_id):
                                # elem.update({"node": peer_id, "status": True})    
                                self.links[str(peer_id)].send([type, msg, shortestPath, self.vectorClock, message_id, origin])
                                
                                #self.pending_acks[type].update({message_id:0})
                            case "BC":
                                if (origin == None):
                                    origin = self.id
                                
                                self.pending_fwd_acks[message_id].append({"node": peer_id, "status": False})    
                                self.links[str(peer_id)].send(["BC", msg, shortestPath, self.vectorClock, message_id, origin])                                
                                
                            case "SIMPLE":
                                if(len(shortestPath) == 1):
                                    # print(f"Node {self.id} => {self.links}")
                                    # in this case, shortestPath is a list of only ONE element that corresponds to the sink !!!
                                    self.links[str(peer_id)].send(["SIMPLE", msg, shortestPath, self.vectorClock, message_id, origin])    
                                else:
                                    self.links[str(peer_id)].send(["SIMPLE", msg, shortestPath, self.vectorClock, message_id])
                                
                                # here it is not needed the "origin" field since it is possible to retrieve it from shortestPath and is needed
                                # only one ack!
                                self.pending_acks["ACK"].update({message_id:0})
                        
                        FOUND = True
                        # print(f"Node {self.id} > {self.sent_to}")
                        self.sent_to[message_id][peer_id].append([shortestPath, origin])

                        typeOf = "send-"+type
                        self.eventGenerating(msg, typeOf)
                        
                        #self.pending_acks[message_id] = (msg, shortestPath, peer_id, time.time())
                        # self.ack_flags[message_id] = False  # Initialize ack flag to False
                        # self.message_sent_flags[message_id] = True  # Mark message as sent
                        
                        #print(f"Node {self.id} sent message {msg} with ID {message_id} to {peer_id}")
                        #self.event_set[len(self.event_set) - 1]
                        break
                
                if FOUND == False:
                    if len(shortestPath) == 1:
                        print("This should be not possible to be reached")
                        
                        # this case may not be possible to be reached because of implementation constraints
                        # self.sendMsgBC(msg) ### WARNING! It will generate an infinite loop of recursions!!!
                    else:
                        idx = shortestPath.index(self.id) + 1
                    # print("idx:", idx)
                    
                        if(idx < len(shortestPath)):
                            next_hop = shortestPath[idx]
                            
                            if(next_hop in self.sent_to[message_id]):
                                if([shortestPath, origin] in self.sent_to[message_id][next_hop]):
                                    print(f"Node {self.id} > [FOUND = False] - {message_id} previously sent to {next_hop}, aborting send...")
                                    pass
                            
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
                                    
                                    self.links[str(elem['neigh'])].send(str([type, msg, shortestPath, self.vectorClock, message_id]))
                                    
                                    typeOf = "send-" + type
                                    self.eventGenerating(msg, typeOf)
                                    
                                    self.pending_acks["ACK"].update({message_id:0})
                                    
                                    # self.pending_acks[message_id] = (msg, shortestPath, elem['neigh'], time.time())
                                    # self.ack_flags[message_id] = False  # Initialize ack flag to False
                                    # self.message_sent_flags[message_id] = True  # Mark message as sent
                                    
                                    #print(f"Node {self.id} forwarded message {msg} with ID {message_id} to {elem['neigh']}")
                                    typeOf = "send-" + type
                                    self.sent_to[message_id][next_hop].append([shortestPath, origin])
                                    self.eventGenerating(msg, typeOf)
                                    break
                        
                    # OLD IMPLEMENTATION
                    # for elem in self.neighbors:
                    #     print(f'{self.id}: [searching NEAREST NEIGHBOR] {shortestPath[]} vs {elem["neigh"]} -> {elem["neigh"] == shortestPath[0]}')
                    #     if elem["neigh"] == shortestPath[0]: 
                    #         shortestPath.pop(0)
                    #         self.links[str(elem['neigh'])].send(str([msg, shortestPath]))
                
        # except Exception as e:
        #     print(f"\tRaised: {e}")
            # print(f"Stacktrace::: {traceback.print_exc()}")
            # print(f"Impossible to send a message to specified peer - {e}")
    
    def spawn_terminal(self):
        self.running = True
        self.listener_thread = threading.Thread(target=self.listen_msg)
        self.listener_thread.start()
        
        self.input_thread = threading.Thread(target=self.handle_input)
        self.input_thread.start()

    # for each of the link, it listens for possible incoming messages
    def listen_msg(self, link):
        #try:
            # context = zmq.Context()
            # receiver = context.socket(zmq.PULL)
            # receiver.bind(f"tcp://{self.address}:{port}")
            # print(f"starting listening at {self.address}:{port} ...")
            
            while not(self.stop_event.is_set()):
                message = link.recv()
                
                if message is not None:
                    print(f"Node {self.id} > recv {message} ", end = "")
                    self.messageLog.append(message)
                                        
                    reconstructed_payload = ast.literal_eval(message)
                    
                    type = reconstructed_payload[0]
                    if type not in {"ACK", "ACK_BC", "SIMPLE", "BC"}:
                        print("Invalid message!!")
                        return
                    
                    msg = reconstructed_payload[1]
                    shortPath = reconstructed_payload[2]
                    vc = reconstructed_payload[3]
                    message_id = reconstructed_payload[4]
                    
                    self.manage_vector_clock(vc)
                    self.vectorClock[self.id] += 1
                                        
                    # TODO
                    typeOf = "receive-" + type
                    self.eventGenerating(msg, typeOf)
                    
                    # wide usage of switch-case pattern for recognise type of message listened
                    match type:
                        
                        # case for simple message to send to a certain node, it behaves as usual
                        case "SIMPLE":
                            if(len(shortPath) > 1):
                                
                                node_id = shortPath[shortPath.index(self.id) - 1]
                                print(f"from {node_id}")
                                
                                if(node_id not in self.received_with_id):
                                    self.received_with_id[node_id] = {}
                                
                                if(message_id not in self.received_with_id[node_id]):
                                    self.received_with_id[node_id][message_id] = []
                                
                                if([shortPath, shortPath[0]] in self.received_with_id[node_id][message_id]):
                                    break
                                
                                self.received_with_id[node_id][message_id].append([shortPath, shortPath[0]])
                                
                                if(self.id != shortPath[-1]):
                                    next_hop = shortPath[shortPath.index(self.id) + 1]
                                    print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Node {self.id} forwarding {message} to {next_hop}")
                                    self.send_to(type, next_hop, msg, shortPath, message_id, shortPath[0])
                                
                                else:
                                    shortPath = shortPath[::-1]
                                    if(msg == "HeartBeatRequest"):
                                        msg = "HeartBeatReply"
                                        
                                    self.send_to("ACK", shortPath[shortPath.index(self.id) + 1], msg, shortPath, message_id, shortPath[0])
                            
                            elif(len(shortPath) == 1):
                                origin = reconstructed_payload[5]
                                peer_id = -1
                                
                                for elem in self.neighbors:
                                        # print(f"found: {self.links[str(elem['neigh'])]} vs {link}")
                                        if(self.links[str(elem["neigh"])] == link):
                                            peer_id = elem["neigh"]
                                            FOUND = True
                                            break
                                        
                                if(not FOUND):
                                    print(f"Node {self.id} : No neighbor found, exiting...")
                                    break
                                        
                                print(f"from {peer_id}")
                                
                                ALREADY_RECVD = False
                                
                                for elem in self.received_with_id:
                                    # for el in self.received_with_id[elem][message_id]:
                                    if(message_id in self.received_with_id[elem]):
                                        if([shortPath, origin] in self.received_with_id[elem][message_id]):
                                            ALREADY_RECVD = True
                                            break
                                
                                if(not ALREADY_RECVD):
                                    
                                    if(peer_id not in self.received_with_id):
                                        self.received_with_id[peer_id] = {}
                                    
                                    if(message_id not in self.received_with_id[peer_id]):
                                        self.received_with_id[peer_id][message_id] = []
                                        
                                    self.received_with_id[peer_id][message_id].append([shortPath, origin])
                                        
                                    if(shortPath[0] == self.id):
                                        if(msg == "HeartBeatRequest"):
                                            msg = "HeartBeatReply"
                                            
                                        self.send_to("ACK", peer_id, msg, [origin], message_id, self.id)
                                    
                                    else:
                                        # print(f"\nNode {self.id}  > MESSAGE NOT FOR ME :(\n")
                                        if(message_id not in self.fwd_senders):
                                            self.fwd_senders.update({message_id: peer_id})
                                        
                                        for neigh in self.neighbors:
                                            if((neigh['neigh'] != peer_id) and (neigh['neigh'] != origin) and (neigh['neigh'] != self.fwd_senders[message_id])):
                                                self.send_to(type, neigh['neigh'], msg, shortPath, message_id, origin)
                            else:
                                print(f"\nError while listening for {type}-message with id {message_id} occurred\n")
                            
                        # case of broadcast message: it searches the neighbor and it will send to it the msg, otherwise it broacasts it
                        case "BC":
                            origin = reconstructed_payload[5]
                            peer_id = 0
                            
                            if(peer_id not in self.received_with_id):
                                    self.received_with_id[peer_id] = {}
                                
                            if(message_id not in self.received_with_id[peer_id]):
                                    self.received_with_id[peer_id][message_id] = []
                                    
                            if([shortPath, origin] in self.received_with_id[peer_id][message_id]):
                                    break
                                    
                            self.received_with_id[peer_id][message_id].append([shortPath, origin])
                            
                            for elem in self.neighbors:
                                # print(f"found: {self.links[str(elem['neigh'])]} vs {link}")
                                if(self.links[str(elem["neigh"])] == link):
                                    peer_id = elem["neigh"]
                            
                            self.sendMsgBC(msg, message_id, origin, peer_id)
                            # print(f"{self.id} sends to {len(self.neighbors)} nodes")
                            
                        # case for ack for broadcast: update status for neighbor that sends ack then check if it has received all acks needed
                        case "ACK_BC":
                            # print("received an ACK_BC")
                            peer_id = self.get_node_id_by_link(link)
                            FOUND = False
                            
                            for elem in self.pending_fwd_acks[message_id]:
                                # print(f"Node {self.id} -> {int(elem['node'])} == {int(peer_id)} : {int(elem['node']) == int(peer_id)}")
                                if(int(elem["node"]) == int(peer_id)):
                                    FOUND = True
                                    elem.update({"status": True})
        
                            if(not FOUND):
                                print("Something wrong")
                                return

                            origin = reconstructed_payload[5]
                            
                            if(self.check_pending_acks_customized(message_id)):
                                if(origin == self.id):
                                    self.termination_print()
                                    # self.stop_event.set()
                                else:
                                    self.send_to(type, self.pending_acks[message_id]["fwd"], msg, [self.id], message_id, origin)
                            else:
                                print("TBD")
                                pass
                                # self.sendMsgBC(msg, message_id, origin, shortPath)
                                
                        # case for simple msg ack: simply check the node to forward the ack
                        case "ACK":

                            if(len(shortPath) > 1):
                                if(shortPath[-1] == self.id):
                                    print("", end = "")
                                    # self.stop_event.set()
                                else:
                                    next_hop = shortPath[shortPath.index(self.id) + 1]
                                    
                                    node_id = shortPath[shortPath.index(self.id) - 1]
                                
                                    if(node_id not in self.received_with_id):
                                        self.received_with_id[node_id] = {}
                                    
                                    if(message_id not in self.received_with_id[node_id]):
                                        self.received_with_id[node_id][message_id] = []
                                    
                                    if([shortPath, shortPath[0]] in self.received_with_id[node_id][message_id]):
                                        break
                                    
                                    self.received_with_id[node_id][message_id].append([shortPath, shortPath[0]])
                                
                                    print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Node {self.id} forwarding {message} to {next_hop}")
                                    
                                    self.vectorClock[self.id] += 1
                                    self.send_to(type, next_hop, msg, shortPath, message_id, shortPath[0])  # Use the same message ID
                                    
                                    # typeOf = "send"
                                    # self.eventGenerating(msg, typeOf)
                            else:
                                origin = reconstructed_payload[5]

                                for elem in self.neighbors:
                                    # print(f"found: {self.links[str(elem['neigh'])]} vs {link}")
                                    if(self.links[str(elem["neigh"])] == link):
                                        peer_id = elem["neigh"]
                                    
                                print(f"from {peer_id}")

                                if(shortPath[0] == self.id):

                                    if(peer_id not in self.received_with_id):
                                        self.received_with_id[peer_id] = {}
                                
                                    if(message_id not in self.received_with_id[peer_id]):
                                        self.received_with_id[peer_id][message_id] = []
                                        
                                    ALREADY_SENT = False

                                    #print("\nself.sent_to[message_id]: ", self.sent_to[message_id])
                                    # print("\nself.sent_to[message_id][self.fwd_senders[message_id]]: ", self.sent_to[message_id][self.fwd_senders[message_id]])
                                                                      
                                    for elem in self.received_with_id:    
                                        print(f"self.received_with_id[elem]: {self.received_with_id[elem]}")
                                        if(message_id in self.received_with_id[elem]):
                                            if([shortPath, origin] in self.received_with_id[elem][message_id]):
                                                ALREADY_SENT = True
                                                break
                                                                        
                                    if(ALREADY_SENT == True):
                                        break
                                    
                                    self.received_with_id[peer_id][message_id].append([shortPath, origin])
                                    
                                    if(msg == "HeartBeatReply"):
                                        # print("Appending to pfd queue")
                                        self.pfd.append_ack(message_id, origin)
                                    
                                    else:
                                        self.acks_received[message_id].append(origin)
                                        
                                    print(self.acks_received[message_id])
                                    
                                    if(len(self.acks_received[message_id]) == (self.node_into_network - 1)):
                                        print(self.acks_received[message_id])
                                        print(f"\nNode {self.id} : self.acks_received[{message_id}]: {self.acks_received}\n")
                                        print(f"Node {self.id} > STOP")
                                        # self.termination_print()
                                        # self.stop_event.set()
                                        
                                    # self.termination_print()
                                    
                                else:
                                    
                                    # print(f"Node {self.id} : self.fwd_senders[{message_id}]: {self.fwd_senders[message_id]}")
                                    self.send_to(type, self.fwd_senders[message_id], msg, shortPath, message_id, origin)                        
                            
                time.sleep(self.delay)
                
        # except Exception as e:
        #     print(f"Catched: {e} while trying to listen at {self.id}:{link}")
        #     # print(f"Stacktrace::: {traceback.print_exc()}")
        # finally:
        #     self.cleanup()
    
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
     
    # def handle_input(self):
    #     while self.running:
    #         command = input(f"Node {self.id} > ")
    #         if command.startswith("send"):
    #             _, target_id, message = command.split(maxsplit=2)
    #             target_id = int(target_id)
    #             self.send_to(target_id, message, shortestPath=[self.id, target_id])  # Provide shortestPath
    #         elif command == "exit":
    #             self.running = False
    #         else:
    #             print("Invalid command")
                                
    def get_neighbors(self):
        return self.neighbors

    def cleanup(self):
        # self.stop_event.set()
        # Set running to False to stop all threads
        self.running = False
        # Join all listener threads to ensure they have finished
        # for thr in self.listener_threads.values():
        #   thr.join() # not useful anymore due to stop event globally notified to each thread
        # Close all links to release resources
        for link in self.links.values():
            link.close()

    # generates event for msg with specified type
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
    
    # check pensing acks for broadcast
    def check_pending_acks_customized(self, message_id):
        cnt = 0
        # print("controllo le acks...")
        # print(f"{message_id} è in pending_fwd_acks? {message_id in self.pending_fwd_acks}")
        # print(self.pending_fwd_acks[message_id])
        if message_id in self.pending_fwd_acks:
            for elem in self.pending_fwd_acks[message_id]:
                # print(f"Key: {node}, Value: {status}")
                # for elem in self.pending_fwd_acks[message_id]:
                # print(node, status)
                # print(elem)
                if(elem["status"] == False):
                    # print("returning F")
                    return False
                cnt += 1
            # print(f"Node {self.id} > #acks for {message_id}: {cnt}")
            # print("returning T")
            return True
        
        # print("returning F")
        return False
        
    
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
    def handle_received_ack(self,type, message_id, shortPath):
    # Check if the ack is for a pending message
        if message_id in self.pending_acks[type]:            
            cnt = self.pending_acks[type][message_id]
            
            if(cnt == len(self.neighbors)):
                print("I'm lost :_( ")
                ## self.send_to("ACK_BC", shortestPath[0], ms)
            
            # (msg, shortestPath, peer_id, timestamp) = self.pending_acks[message_id]
        
            # # Find the index of the current node in the path
            # index = shortestPath.index(self.id)
        
            # # If the current node is not the first in the path
            # if index > 0:
            #     # The previous node is the leftmost node in the path
            #     next_hop = shortestPath[index - 1]
            
            #     # Send ack to previous node
            #     self.send_ack(self.links[str(next_hop)], message_id)
            #     print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Node {self.id} sending ack for message ID {message_id} to {next_hop}")
            #     #print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Node {self.id} received ack from {peer_id} and sending ack to {next_hop} for message ID {message_id}")

    # function that sends a message generated by an origin
    def sendMsgBC(self, msg, msg_id, origin, sp):
        type = "BC"
        self.pending_acks[msg_id] = {"origin": origin, "fwd": sp}
        some_neighbors_exists = False
                
        self.pending_fwd_acks[msg_id] = []
                
        for neigh in self.neighbors:
            # print(f"{neigh['neigh']} != {origin} --> {(neigh['neigh'] != origin)}")
            # print(f"{neigh['neigh']} != {sp} --> {neigh['neigh'] != sp}\n")
            if(neigh["neigh"] != origin and neigh["neigh"] != sp):
                some_neighbors_exists = True
                self.send_to(type, neigh["neigh"], msg, [self.id], msg_id, origin)
                
        
        print(f"\nNode {self.id} > waiting for {self.pending_fwd_acks}\n")
        
        if(not(some_neighbors_exists)):
            print(f"Node {self.id} > no neighbor to send ")
            #if(not(self.check_pending_acks_customized(msg_id))):
            self.send_to("ACK_BC", sp, msg, self.id, msg_id, origin)
                # self, type, peer_id, msg, shortestPath, message_id, origin
    
    def specialBC_Node(self, msg, msg_id):
        type = "SIMPLE"
        if(msg_id == None):
            msg_id = str(uuid.uuid4())
    
        self.acks_received[msg_id] = []
        
        for neigh in self.neighbors:
            for i in range(0, self.node_into_network):
                if(i != self.id):
                    self.send_to(type, neigh['neigh'], msg, [i], msg_id, self.id)
    
    # simulation of perfect failure detector
    def pfd_caller(self):
        msg_id = str(uuid.uuid4())
        self.pfd.start_pfd(self.corrects, msg_id, self.delay * (2 * self.node_into_network))
        self.specialBC_Node("HeartBeatRequest", msg_id)
        
        time.sleep(self.delay * (2 * self.node_into_network + 1))
        
        if(self.pfd.get_flag()):
            print(f"pfd.get_flag = {self.pfd.get_flag()} - corrects : {self.pfd.get_new_corrects()}")
            self.corrects = self.pfd.get_new_corrects()
            print(f"Node {self.id} > new corrects: {self.corrects}")
        
        elif(self.pfd.get_flag() == "AUG_DELAY"):
            self.pfd_caller()    
            
    
    # prints vc, ml and es for debugging purposes          
    def termination_print(self):
        print("Vector clock: ", self.vectorClock)
        
        print("Message log: ")
        for elem in self.messageLog:
            print("\t", elem)
        
        print("Event set: ")
        for elem in self.event_set:
            print(f"\t[type: {elem.get_type()}, index: {elem.get_index()}, ts: {elem.get_ts()}]")