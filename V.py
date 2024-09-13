# #Matrix to keep store the dynamic matrix for vector clock
# import math
# class V:
#     def __init__(self, n): #n è un array di processi coinvolti
#          #columns are the P and row the events of that process P -- I need to create a new row for every
#         #event, then I update also the receiving
#         self.processes = []
#         #self.processes = n
#         self.lenProcesses = len(n) 
#         self.matrix = []

#         for process in n:
#             self.processes.append(process) #Mi inizializo gli le righe di ogni matrice
        
#         for process in n:
#             init = []
#             init.append(self.processes) #[P1, P2, P3, ... , Pn]
#             init.append([0] * self.lenProcesses) #[0, 0, 0, ..., 0] * len(P)
#             self.matrix.append(init) #Instanzio la matrice con valori iniziali 0,0,0... e i rispettivi processi sopra

#     def update(self, process_sender_index, process_recvr_index):
#             previous_sender = self.matrix[process_sender_index][len(self.matrix[process_sender_index]) - 1].copy() #Mi faccio la copia cosi da ritornare il precedente per poi aggiornarlo
#             previous_sender[process_sender_index] += 1 
#             self.matrix[process_sender_index].append(previous_sender)

#             previous_recver = self.matrix[process_recvr_index][len(self.matrix[process_recvr_index]) - 1].copy()
#             previous_recver[process_recvr_index] += 1
#             previous_recver[process_sender_index] = self.matrix[process_sender_index][len(self.matrix[process_sender_index]) - 1][process_sender_index]
#             self.matrix[process_recvr_index].append(previous_recver)
#             #self.matrix[process_called_index].append(self.matrix[process_called_index][len(self.matrix[process_called_index]) - 1][process_called_index] += 1)
#             #self.matrix[process_called_index].append()
#             #eventRow = self.matrix[process_called_index][]
        
#     def getMaxID(self):
#         maxP = [0] * self.lenProcesses
#         for i in range(self.lenProcesses):
#             for j in range(self.lenProcesses):
#                 #print(f" HERE WE GO: {self.matrix[j][len(self.matrix[j] - 1)][i]}")
#                 maxP[i] = max(maxP[i], self.matrix[j][len(self.matrix[j]) - 1][i])
        
#         return maxP #Ritorna l'array di maximum value per ogni processo
    
#     def printMatrix(self):
#         for p in range(self.lenProcesses):
#             for j in range(len(self.matrix[p])):
#                 if(j == 0):
#                     print(f"EVENT {p} --> [P1, P2, P3]") #Da cambiare ovviamente
#                 else:
#                     print(f"EVENT {p} --> {self.matrix[p][j]}")

# #########PROVA############
# matrix = V([1,2,3])

# print("CIAO")

# matrix.update(1,2)
# matrix.update(0,2)
# matrix.update(0,1)

# matrix.printMatrix()

# maxs = matrix.getMaxID()

# #print(f"LAST MATRIX: {matrix}")
# print(f"MAX VALUE\n[P1,P2,P3]:\n{maxs}")

# #TO LET IT WORKS DO: "python V.py " OR for linux users: "python3 V.py"

class V:
    def __init__(self, procs):
        self.n = len(procs)
        self.processes = procs
        self.matrix = []
    
    def update_send(self, sendr_id, recvr_id, seq_n):
        if((sendr_id in self.processes) and (recvr_id in self.processes)):
            tmp = []
            if(len(self.matrix) > 0):
                tmp = self.matrix[len(self.matrix) - 1].copy()
            else:
                tmp = [0] * (len(self.processes))

            tmp[self.processes.index(sendr_id)] = seq_n
            # tmp[self.processes.index(recvr_id)] += 1

            self.matrix.append(tmp)


    def update_recv(self, sendr_id, recvr_id, seq_n):
        if((sendr_id in self.processes) and (recvr_id in self.processes)):
            tmp = []
            if(len(self.matrix) > 0):
                tmp = self.matrix[len(self.matrix) - 1].copy()
            else:
                tmp = [0] * (len(self.processes))

            tmp[self.processes.index(sendr_id)] = seq_n
            tmp[self.processes.index(recvr_id)] += 1

            self.matrix.append(tmp)

    def get_max_sn(self, id):
        if(id in self.processes):
            if(len(self.matrix) == 0):
                return 0
            return self.matrix[len(self.matrix) - 1][self.processes.index(id)]
        return False

    def get_num_procs(self):
        return len(self.processes)
    
    def get_val(self, i, j):
        if((i >= self.n) or (j >= self.n)):
            print("Incompatible indexes!")
            return None
        
        return self.matrix[i-1][j]
    
    def copy(self):
        to_be_ret = V(self.processes)
        to_be_ret.matrix = self.matrix.copy()
        return to_be_ret

    def print_matrix(self):
        print("V:", end = "\nprocs:\t")
        
        for proc in self.processes:
            print(proc, end = " ")
        print("", end = "\n")
        print("-------------------------", end = "\n")

        for elem in self.matrix:
            print(f"e{self.matrix.index(elem)}\t", end = "")
            for e in elem:
                print(e, end = " ")
            print("", end = "\n")
        print()

# v = V([1, 2, 3])
# v.print_matrix()
# v.update(1, 2, (v.get_max_sn(1) + 1))
# v.print_matrix()

# v.update(2, 3, (v.get_max_sn(2) + 1))
# v.print_matrix()

# v.update(3, 1, (v.get_max_sn(3) + 1))
# v.print_matrix()

# v.update(1, 3, (v.get_max_sn(1) + 1))
# v.print_matrix()
