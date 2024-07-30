import threading
import traceback
import time
import ast
import os
import signal

from pp2p import PerfectPointToPointLink

class Node:
    def __init__(self, my_id, my_addr, neighbors, all):
        self.id = my_id
        self.links = {}
        self.address = my_addr
        self.node_into_network = int(all)
        
        self.vectorClock = [0] * (self.node_into_network + 1)
        self.messageLog = []
        
        self.neighbors = neighbors
        
        self.listener_threads = {}
        self.stop_event = threading.Event()
        
        # print(f"neighbors into {self.id} : {neighbors}")
        # print(self.id, " -> ", neighbors)
        
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
        for i in range(0, self.node_into_network):
            if(self.vectorClock[i] < vc[i]):
                self.vectorClock[i] = vc[i]
        
    def send_to(self, peer_id, msg, shortestPath):
        try:
            if not(isinstance(peer_id, str)):      
                FOUND = False
                for elem in self.neighbors:
                    # print(f'{self.id}: {peer_id} vs {elem["neigh"]} -> {elem["neigh"] == peer_id}')
                    # print("debugging: ", self.links[str(elem['neigh'])])
                    # print("link: ", self.links.keys(elem["neigh"]))
                    
                    if elem["neigh"] == peer_id:
                        # print(f"{self.id} - {elem["neigh"]}")
                        # print("does exist? ", self.links[str(peer_id)])
                        self.vectorClock[self.id] += 1
                        self.links[str(peer_id)].send([msg, shortestPath, self.vectorClock])
                        FOUND = True
                        break
                
                if FOUND == False:
                    idx = shortestPath.index(self.id) + 1
                    # print("idx:", idx)
                    
                    if(idx == len(shortestPath)):
                        print("Error with indexes!!")
                    
                    else:
                        for elem in self.neighbors:
                            # print(f'{self.id}: [searching NEAREST NEIGHBOR] {shortestPath[idx]} vs {elem["neigh"]} -> {elem["neigh"] == shortestPath[idx]}')
                
                            # DIFFERENT WAY TO MOVE INTO 'shortestPath' variable:
                            #   using the method 'index[x]' it can be possible to find
                            #   the index of object 'x' into it, so, this can be useful for avoiding
                            #   element deletion from that variable (can be reused for ack of reception!!!)
                            
                            if elem["neigh"] == shortestPath[idx]: 
                                self.vectorClock[self.id] += 1
                                self.links[str(elem['neigh'])].send(str([msg, shortestPath, self.vectorClock]))
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
        try:
            # context = zmq.Context()
            # receiver = context.socket(zmq.PULL)
            # receiver.bind(f"tcp://{self.address}:{port}")
            # print(f"starting listening at {self.address}:{port} ...")
            
            while not(self.stop_event.is_set()):
                message = link.recv()
    
                if message is not None:
                    print(f"\nNode {self.id} > ", end='')
                    
                    reconstructed_payload = ast.literal_eval(message)
                    msg = reconstructed_payload[0]
                    shortPath = reconstructed_payload[1]
                    vc = reconstructed_payload[2]

                    self.manage_vector_clock(vc)
                    
                    if self.id == shortPath[-1]:
                        print(f"received {msg} from {shortPath[0]}")
                        self.vectorClock[self.id] += 1
                        self.stop_event.set()  # send event for stopping threads
                    else:
                        print(f"forwarding {message} to {shortPath[shortPath.index(self.id) + 1]}")
                        self.vectorClock[self.id] += 1
                        self.send_to(shortPath[-1], msg, shortPath)
                                    
                time.sleep(2.0)
                
        except Exception as e:
            print(f"Catched: {e} while trying to listen at {self.id}:{link}")
            # print(f"Stacktrace::: {traceback.print_exc()}")
        finally:
            self.cleanup()
          
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

    def cleanup(self):
        self.stop_event.set()
        # Set running to False to stop all threads
        self.running = False
        # Join all listener threads to ensure they have finished
        # for thr in self.listener_threads.values():
        #    thr.join() # not useful anymore due to stop event globally notified to each thread
        # Close all links to release resources
        for link in self.links.values():
            link.close()