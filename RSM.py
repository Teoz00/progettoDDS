from event_process import EventP

class RSM:
    def __init__(self):
        self.STATE = ["WAITING", "LISTENING", "BUSY", "EXECUTING"] #MACRO -- per ogni stato passato dal server mi serve un checksum
        self.ACTUAL_STATE = None
        self.ACTIONS = ["SUM", "MULL", "DIVIDING"] #Basic operations
        self.event = set() #EventInputs -- replicas at most 2N + 1 
        self.correct = []
        self.faulty = []
        self.inputLog = [] # for every event following the code order
        self.checkpoint = {} #events catcher / backupEvetns -- dizionario di liste {"event" : [ts,state]}
        self.output = []
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
        self.ACTUAL_STATE = "BUSY"
        self.event.add(event) 
        self.correct.append(event)
        #print(self.correct)
        self.checkpoint = {event : [event.get_ts(), event.type] } #mi salvo il timestamp
        self.inputLog.append(event) #I keep trace of my input
        self.ACTUAL_STATE = "LISTENING"

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

    def join():
        pass

    def restore(self, event):
        self.addEvent(EventP(event.getEventCheck()))

    def typeFun(self, value): #example function / better 
        return type(value) 
    
    def funOperation(self, type, a, b): 
        match type:
            case "SUM" :
                return a + b
            case "MULL":
                return a * b
            case "DIVIDE":
                return a / b
    
    def outputGenerator(self, inputFunction):
        for e in self.correct:
            self.output.append(inputFunction(e))

    def checkCorrectness(self, inputFunction): #inputFunction is fun / I think I need the consensous!
        self.outputGenerator(inputFunction)

        for elem in range(len(self.output)):
            for elem2 in range(len(self.output)):
                if self.output[elem] == self.output[elem2]:
                    print("Correct")
                else:
                    print("NOT Correct")
                    print(f"|CORRECT BEFORE: {self.correct}|")
                    print(f"********************\nRSM --> faulty\nThe following output1 /{self.correct[elem]}/: {self.output[elem]}\nis different by output2 /{self.correct[elem2]}/ {self.output[elem2]}\n********************")
                    self.correct.remove(self.correct[elem2])
                    print (f"|CORRECT AFTER: {self.correct}|")
                    return False
        return True

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
rsm = RSM()

event1 = EventP("send", 1, [4, 3, 5], "Ciao1")
event2 = EventP("send", 1, [4, 3, 5], "Ciao2")
 
#rsm.addEvent("1")
#rsm.addEvent("2")
#rsm.addEvent(3)
rsm.addEvent(event1)
rsm.addEvent(event2) 

rsm.checkCorrectness(rsm.typeFun)
##################################################

