from event_process import EventP

class RSM: # p_i,a
    def __init__(self, num_nodes):
        self.STATE = ["WAITING", "JOIN", "QUIT", "CHECKPOINT"] #MACRO -- per ogni stato passato dal server mi serve un checksum
        self.ACTUAL_STATE = None
        self.ACTIONS = ["SUM", "MULL", "DIVIDING"] #Basic operations
        
        self.event = set() #EventInputs -- replicas at most 2N + 1 
        
        self.correct = []
        self.faulty = []
        
        self.inputLog = [] # for every event following the code order
        self.checkpoint = {} #events catcher / backupEvetns -- dizionario di liste {"event" : [ts,state]}
        self.output = []

        self.ts = 0 # seq_i,a
        self.num_nodes = num_nodes
        self.internal_vector_clock = [0] * num_nodes

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

    def handle_event(self, event):
        # print("event", event)
        type = event.get_type()
        id = event.get_id()

        match type:
            case "SEND":
                self.update_vc(id)
                self.ts += 1
            
            case "RECV":
                self.update_vc(id)
                self.ts += 1
            
            case 'CRASH':
                i = 0
                
                while i < self.num_nodes:
                    if(i != int(id)):
                        self.update_vc(id)
                        self.ts += 1 # rivedere, strano...
                    
                    i += 1

        event.set_index(self.ts)
        event.set_timestamp(self.internal_vector_clock)
        # event.print_event()

    def addEvent(self, event):
        self.ACTUAL_STATE = "BUSY"
        
        self.event.add((event, event.get_msg()))
        # self.handle_event()
        self.correct.append(event)
        #print(self.correct)
        self.checkpoint = {event : [event.get_ts(), event.type] } #mi salvo il timestamp
        self.inputLog.append(event) #I keep trace of my input
        
        self.ACTUAL_STATE = "LISTENING"

    def updateEvent(self,event):
        self.checkpoint = {event : [event.get_ts(), event.ACTUAL_STATE]}

    def setInput(self, event_set):
        for event in event_set:
            self.handle_event(event)
            self.addEvent(event)
        
        # for elem in self.correct:
        #     elem.print_event()

        return True

    def getEventCheck(self, event):
        return self.checkpoint[str(event)]

    def getState(self):
        return self.ACTUAL_STATE #oppure self.ACTUAL_STATE TODO

    def get_vector_clock(self):
        return self.internal_vector_clock

    def reconfiguration(self, checkpoint, corrects, faulties, log):
        # from Wikipedia.com :
        # Reconfiguration allows replicas to be added and removed from a system while client requests continue to be processed. 
        # Planned maintenance and replica failure are common examples of reconfiguration. 
        # Reconfiguration involves Quitting and Joining.

        # with interpretation for this project, 
        # reconfiguration in intended as
        # a particular situation of the restart 
        
        self.ACTUAL_STATE = "RECONFIGURING"

        self.correct = corrects
        self.faulty = faulties

        self.output = []
        self.checkpoint = checkpoint
        
        self.inputLog.append(" - RECONFIGURED - ")
        self.inputLog.append(log)

        self.ACTUAL_STATE = "RECONFIGURED"
         
    #def quitting(self, eventToRemove):
        #neigh = eventToRemove.neighbors
        #if (len(neigh) >= 0):
         #   before = neigh[0]
         #   if (len(neigh) >= 1): 
         #       after = neigh[1]
         #       before.neighbors.add(after)
         #       after.neighbors.add(before)
         #       before.neighbors.remove(eventToRemove)
         #   else:
         #       before.neighbors.remove(eventToRemove)

        #self.event.remove(eventToRemove)
    #restart, restore or new
    def join(self, event, type):
        match type:
            case "RESTART", "NEW":
                self.ACTUAL_STATE = type
                self.updateEvent(event)
                self.inputLog(type+"ED: "+event) #to handle with a parsing 
            case "RESTORE":
                self.ACTUAL_STATE = "RESTORE"
                self.updateEvent(self.checkpoint)
                self.inputLog("RESTORED: "+event) #Parsing


    def restore(self, event):
        self.addEvent(EventP(event.getEventCheck()))

    def typeFun(self, value): #example function / better 
        return type(value) 
    
    # simulation of send/recv/crash for executing a list of operations
    def funOperation(self, type, a, msg): 
        match type:
            case "SEND", "RECV":
                self.update_vc(a)
                self.addEvent(EventP(self.ts, (len(self.event) - 1), self.internal_vector_clock, str([type, a, msg])))
                self.ts += 1
            
            case "CRASH":
                i = 0
                
                while i < self.num_nodes:
                    if(i != int(a)):
                        self.update_vc(i)
                        self.addEvent(EventP(self.ts, (len(self.event) - 1), self.internal_vector_clock, str(["RECV", a, type])))
                        self.ts += 1
                    
                    i += 1


    def outputGenerator(self, inputFunction, type, a, msg):
        for e in self.correct:
            self.output.append(inputFunction(type, a, msg))

    def checkCorrectness(self): 
        #inputFunction is fun / I think I need the consensous! -- QUIT
        # check if its final result is the same of the agreed one after consensus
        
        for e in self.correct:
            self.outputGenerator(self.funOperation, e.get_type(), e.get_id(), e.get_msg())

        for elem in range(len(self.output)):
            for elem2 in range(len(self.output)):
                if self.output[elem] == self.output[elem2]:
                    print("Correct")
                else:
                    self.ACTUAL_STATE = "QUIT"
                    print("NOT Correct")
                    print(f"|CORRECT BEFORE: {self.correct}|")
                    print(f"********************\nRSM --> faulty\nThe following output1 /{self.correct[elem]}/: {self.output[elem]}\nis different by output2 /{self.correct[elem2]}/ {self.output[elem2]}\n********************")
                    self.checkpoint = {self.correct[elem2] : [self.correct[elem2].get_ts(), self.correct[elem2].type] }
                    self.faulty.add(self.correct[elem2])
                    self.correct.remove(self.correct[elem2])
                    print (f"|CORRECT AFTER: {self.correct}|")
                    return False
        
        return True

    def update_vc(self, node):
        self.internal_vector_clock[int(node)] = self.internal_vector_clock[int(node)] + 1

    def printEvent(self, type):
        # print("self.event: ", self.event)
        match type:
            case "bc":
                if(len(self.event) != 0):
                    for events in self.event:
                        print(f"Event {events} > index: {str(events.get_index())}\t type: {str(events.get_type())}")
            case "test":
                pass


###############################################################
#NB, per usare questo test, commentare |self.checkpoint = {event : [event.get_ts(), "LISTENING"] } #mi salvo il timestamp|
#Ed usare python RSM.py
rsm = RSM(5)

event1 = EventP("SEND", 1, 0, [4, 3, 5], "Ciao1")
event2 = EventP("SEND", 1, 1, [4, 3, 5], "Ciao2")
 
#rsm.addEvent("1")
#rsm.addEvent("2")
#rsm.addEvent(3)
rsm.addEvent(event1)
rsm.addEvent(event2) 

# rsm.checkCorrectness()
##################################################

