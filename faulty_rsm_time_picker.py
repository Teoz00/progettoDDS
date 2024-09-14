from app_graph import ApplicationGraph
import matplotlib.pyplot as plt
import time

case_1 = [2, 5]
case_2 = [3, 4]
case_3 = [2, 4]

################################################
g1 = ApplicationGraph(case_1[0], case_1[1])
t1 = time.time()
g1.check_faulty_rsms()
t1 = time.time() - t1

print("tempo: ", t1)
input("PRESS ENTER TO CONTINUE")

try:
    with open("./rsm_check_faulty_times.txt", 'a') as file:
        file.write(f"time of G(3, 2) : {t1}")
        print("Time added to txt")
except Exception as e:
    print(f"Errore durante l'aggiunta del testo: {e}")


g1.stop_event.set()
g1.cleanup()
################################################

input("PRESS ENTER TO CONTINUE")

################################################
g2 = ApplicationGraph(case_2[0], case_2[1])
t2 = time.time()
g2.check_faulty_rsms()
t2 = time.time() - t2

input("PRESS ENTER TO CONTINUE")

g2.stop_event.set()
g2.cleanup()
################################################

input("PRESS ENTER TO CONTINUE")

################################################
g3 = ApplicationGraph(case_3[0], case_3[1])
t3 = time.time()
g3.check_faulty_rsms()
t3 = time.time() - t3

input("PRESS ENTER TO CONTINUE")

g3.stop_event.set()
g3.cleanup()
################################################

input("PRESS ENTER TO CONTINUE")

print(f"t1 = {t1}\nt2 = {t2}\nt3 = {t3}")