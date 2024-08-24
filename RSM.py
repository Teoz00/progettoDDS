class RSM:
    def __init__(self):
        self.STATE = ["WAITING", "LISTENING", "BUSY", "EXECUTING"] #MACRO -- per ogni stato passato dal server mi serve un checksum
        self.event = set() #EventInputs
        self.inputLog = [] # for every event following the code order
        self.checkpoint = {} #events catcher / backupEvetns
        #self.input  #client request
        #output something
        #ordering among events (Input in same order)  
        #Deterministic
        #visible channel ==> partial/global ordering : Causal order :: guaranted
        #consensous half + 1 min to have confirmed it
        #if failour => error to client (Lentezza o info sbagliate sono una prova della failure)
        #inputLog : tracking of event received as input
        #checkpoint : verify dimension of the log (sizeOf) -- do also tracking to bring the replica 
        #Reconfiguration : add or remnove replicas while client executing /? 
        #Quitting : cancel replica if faulty (replica := nodo)
        #state transfer: bring to current status the replica restored using checkpoint
        #Leader election (Macro node)
        #EXTENSION: 

    def reconfiguration():
        pass

    def quitting():
        pass

    def printEvent():
        pass
        

