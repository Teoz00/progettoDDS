from event_process import EventP

class RSM:
    def __init__(self):
        self.STATE = ["WAITING", "LISTENING", "BUSY", "EXECUTING"] #MACRO -- per ogni stato passato dal server mi serve un checksum
        self.ACTUAL_STATE = None
        self.event = set() #EventInputs
        self.inputLog = [] # for every event following the code order
        self.checkpoint = {} #events catcher / backupEvetns -- dizionario di liste {"event" : [ts,state]}
        self.output = set()
        #self.input  #client request
        #output something
        #ordering among events (Input in same order)  
        #Deterministic
        #visible channel ==> partial/global ordering : Causal order :: guaranted
        #consensous half + 1 min to have confirmed it
        #if failure => error to client (Lentezza o info sbagliate sono una prova della failure)
        #inputLog : tracking of event received as input
        #checkpoint : verify dimension of the log (sizeOf) -- do also tracking to bring the replica 
        #Reconfiguration : add or remnove replicas while client executing /? 
        #Quitting : cancel replica if faulty (replica := nodo)
        #state transfer: bring to current status the replica restored using checkpoint
        #Leader election (Macro node)
        #EXTENSION: 

    def addEvent(self, event):
        self.event.add(event) 
        self.checkpoint = {event : [event.get_ts(), "LISTENING"] } #mi salvo il timestamp

    def updateEvent(self,event):
        self.checkpoint = {event : [event.get_ts(), event.ACTUAL_STATE]}

    def setInput(self, event_set):
        for elem in event_set:
            self.addEvent(elem)

    def getEventCheck(self, event):
        return self.checkpoint[str(event)]

    def getState(self):
        return self.STATE #oppure self.ACTUAL_STATE TODO

    def reconfiguration(self):
        pass

    def quitting(self, eventToRemove):
        neigh = eventToRemove.neighbors
        if (len(neigh) >= 0):
            before = neigh[0]
            if (len(neigh) >= 1): 
                after = neigh[1]
                before.neighbors.add(after)
                after.neighbors.add(before)
                before.neighbors.remove(eventToRemove)
            else:
                before.neighbors.remove(eventToRemove)

        self.event.remove(eventToRemove)

    def restore(self, event):
        self.addEvent(EventP(event.getEventCheck()))

    def printEvent(self):
        # print("self.event: ", self.event)
        if(len(self.event) != 0):
            for events in self.event:
                print(f"Event {events} > index: {str(events.get_index())}\t type: {str(events.get_type())}")
        

