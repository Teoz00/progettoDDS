import math

class Dijkstra:
    graph = {}
    nodeCost = {}
    parents = {}
    taken = []

    @staticmethod
    def __init__ (graph, nodeCost, parents, type):
        graph = graph
        nodeCost = nodeCost
        parents = parents

      
        Dijkstra.run()

        if type == 0: 
            Dijkstra.result()
        elif type == 1:
            Dijkstra.resultGUI()
        else:
            pass

    @staticmethod
    def minorCostNode():
        minCost = math.inf
        minNodeCost = None 

        for n in Dijkstra.nodeCost:
            singleCostNode = Dijkstra.nodeCost[n]
            if (singleCostNode < minCost) and (n not in Dijkstra.taken):
                minCost = singleCostNode
                minNodeCost = n
            
        return minNodeCost
    
    @staticmethod
    def run():
        node = Dijkstra.minorCostNode()
        while node is not None: 
            nodeCost = Dijkstra.nodeCost[node]  # costo nodo corrente.
            neighbor = Dijkstra.graph[node]  # ricavo i nodi vicini
            for n in neighbor.keys():
                x = str(n)
                newNodeCost = nodeCost + neighbor[x]  # costo per arrivare al nodo che sto esaminando.
                if Dijkstra.nodeCost[x] > newNodeCost:
                    Dijkstra.nodeCost[x] = newNodeCost
                    Dijkstra.parents[x] = node
            Dijkstra.taken.append(node)  # inserisco il nodo appena processato in questo array in modo da non creare loop.
            node = Dijkstra.minorCostNode()

    @staticmethod
    def getLastNode():
        tmp = ""
        for item in Dijkstra.parents.keys():
            tmp = item
        return tmp

    @staticmethod
    def getFirstNode():
        for item in Dijkstra.graph.keys():
            return item

    @staticmethod
    def printPath():
         # Separiamo le chiavi ed i rispettivi valori in due vettori differenti.
        val = []
        key = []
        outTMP = []
        for item in Dijkstra.parents.keys():
            key.append(item)
        for item in Dijkstra.parents.values():
            val.append(item)
        # Debug:
        # print("KEY: ", key)
        # print("VAL: ", val)

        a = len(key) - 1
        i = 0
        x = a
        while i < a:  # Creazione dell'output definitivo per il percorso da seguire.
            try:
                v = val[x]
                outTMP.append(v)
                x = key.index(v)
            except:
                break
            i += 1

        out = ""
        for item in range(len(outTMP) - 1, -1, -1):
            out += outTMP[item] + " -> "
        out += Dijkstra.getLastNode()
        return out.upper()

    @staticmethod
    def result():
        print("Graph: ", Dijkstra.graph)
        print("Parents: ", Dijkstra.parents)
        print("Path: ", Dijkstra.printPath())

    @staticmethod
    def resultGUI():
        return [Dijkstra.graph, Dijkstra.parents, Dijkstra.printPath()]

    