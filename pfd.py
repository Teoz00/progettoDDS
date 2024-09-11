import threading
import time

class PerfectFailureDetector:
    
    def __init__(self):
        self.corrects = []
        self.received_acks = []
        self.last_msg_id = ''
        self.listening_thread = None
        self.stop_event = threading.Event()
        self.delay = 0
        self.flag = False
        
    def start_pfd(self, corr, msg_id, delay):
        self.received_acks = []
        self.corrects = corr
        self.last_msg_id = msg_id
        self.delay = delay
        
        self.listening_thread = threading.Thread(target=self.waiting_thread_function)
        self.listening_thread.start()   
    
    def waiting_thread_function(self):
        time.sleep(self.delay)
        self.flag = False
        # self.stop_event.set()
            
        temp_list = []
        
        for elem1 in self.corrects:
            # print("PFD - received acks: ", self.received_acks)
            for elem2 in self.received_acks:
                if(elem1 == elem2):
                    temp_list.append(elem1)
            
            # print("TEMP LIST", temp_list)
        
        if(len(temp_list) == 0):
            self.flag = "AUG_DELAY"
            self.delay = 1.5 * self.delay
            return
        
        # print(f"PFD > replying nodes detected: [{temp_list}]")
        self.corrects = temp_list
        self.flag = True
        
    def append_ack(self, msg_id, node_id):
        # print(f"self.stop_event.is_set() : {self.stop_event.is_set()} -- self.last_msg_id == msg_id : {self.last_msg_id == msg_id}")
        if(not(self.stop_event.is_set()) and (self.last_msg_id == msg_id) and not(node_id in self.received_acks)):
            
            self.received_acks.append(node_id)
    
    def get_flag(self):
        return self.flag
    
    def get_new_corrects(self):
        return self.corrects
