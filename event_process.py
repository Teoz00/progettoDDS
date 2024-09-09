class EventP:
    def __init__(self, t, index, id, vc, msg):
        self.type = t #Send receive
        self.index = index
        self.id = id
        self.ts = vc #NB vc is a vc list
        self.msg = msg

    # ATTENTION!!! id is a scalar clock, not an identifier
    def set_index(self, idx):
        self.index = idx # id

    # ATTENTION!!! ts is a vector, not a scalar
    def set_timestamp(self, tsmp):
        self.ts = tsmp # vc

    def get_type(self):
        return self.type

    def get_index(self):
        return self.index
    
    def get_id(self):
        return self.id
    
    def get_ts(self): 
        return self.ts
    
    def get_msg(self):
        return self.msg
    
    def print_event(self):
        print(f"type : {self.get_type()}, ts : {self.get_index()}, id : {self.get_id()}, vc : {self.get_ts()}, msg : {self.get_msg()}")
