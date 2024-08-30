import ast

class Consensus:
    
    def __init__(self, id, num_nodes):
        
        self.id = id
        self.number_nodes = num_nodes
    
        # self.commanders   = {message_id : commander, ...}
        # self.values       = {message_id: {node_id : value, ...}, ...}
        
        self.commanders = {}
        self.values = {}
        self.chosen_values = {}
    
    def print_status(self, msg_id):
        if(msg_id in self.commanders):
            print(f"Node {self.id} - Consensus_module : status for {msg_id} [{self.commanders[msg_id]} - values: {self.values[msg_id]}]")
    
    # structure of message to handle: [ROLE, VALUE, ]
    def handle_msg(self, message, msg_id, peer_id):
        # print(f"\nNode {self.id} - Consensus_module: {message} received")
        role = message[1]
        value = message[2]
        # print(f"Node {self.id} - Consensus_module: role {role}, value {value}")
        
        if(msg_id not in self.values):
            self.values[msg_id] = {}
        
        if(peer_id not in self.values[msg_id]):
            self.values[msg_id].update({peer_id : value})

        # print(f"\nNode {self.id} - Consensus_module > values = {self.values}")

        if(role == 'COMMANDER'):
            if(msg_id not in self.commanders):
                self.commanders.update({msg_id : peer_id})
                # print(f"\nNode {self.id} - Consensus_module > commanders = {self.commanders}")
                
            return True
                
        elif(role == 'LIEUTANT'):
            self.print_status(msg_id)
            return False

    def choose_value(self, msg_id):
        if(msg_id not in self.values):
            return None
        
        # vals = {node_id : number_of_appearances, ...}
        vals = {}
        
        # accessing each self.values[msg_id][node_id]
        for elem in self.values[msg_id]:
            if(self.values[msg_id][elem] not in vals):
                # it will update vals with the tuple [value obtained from self.values[msg_id][node_id]]
                vals.update({self.values[msg_id][elem] : 1})
            else:
                vals.update({self.values[msg_id][elem] : (vals[self.values[msg_id][elem]] + 1)})
                # print(f"Node {self.id} - Consensus_module : updated {self.values[msg_id][elem]} -> {vals[self.values[msg_id][elem]]}")
                
        
        elected_value = None
        counter = 0
         
        for v in vals:
            if(vals[v] > counter):
                elected_value = v
                counter = vals[v]
            
        self.chosen_values[msg_id] = elected_value
            
        print(f"Node {self.id} - Consensus_module : from {self.values[msg_id]} has been chosen {elected_value}")
        return elected_value

    def agreed_value(self, msg_id):
        if(msg_id in self.values):
            if(len(self.values[msg_id]) == (self.num_nodes - 1)):
                value_to_return = self.choose_value(msg_id)
                
                return value_to_return
    
    def set_value(self, msg_id, value):
        self.commanders[msg_id] = self.id
        self.chosen_values[msg_id] = value
            
    
    def get_commander(self, msg_id):
        # print(f"\nNode {self.id} - Consensus_module > {msg_id} is in {self.commanders}? {msg_id in self.commanders}")
        if(msg_id in self.commanders):
            return self.commanders[msg_id]
        else:
            return None
        
    def check_values(self, msg_id):
        if(msg_id in self.values):
            if(len(self.values[msg_id]) == self.number_nodes - 1):
                return True
            
        return False
    
    def am_I_a_commander(self, msg_id):
        if(msg_id in self.commanders):
            if(self.commanders[msg_id] == self.id):
                return True
        
        return False
    
    def already_chosen(self, msg_id):
        if(msg_id in self.chosen_values):
            return True

        return False
    
    def get_chosen_values(self):
        if(self.chosen_values == {}):
            return False
        
        return self.chosen_values