class EventP:
    def __init__(self, t, index, vc, msg):
        self.type = t #Send receive
        self.index = index
        self.ts = vc #NB vc is a vc list
        self.msg = msg
        
    def get_type(self):
        return self.type

    def get_index(self):
        return self.index
    
    def get_ts(self): 
        return self.ts
    

