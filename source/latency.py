from app_graph import ApplicationGraph
import matplotlib.pyplot as plt
import time

case_1 = [4, 2]

times = []

g1 = ApplicationGraph(case_1[0], case_1[1])

cnt = 3
t1 = time.time()
for j in range(5):
    for i in range(3):
        g1.app_nodes[cnt - i].app_proc_send_to("SIMPLE", i, "latency test", None, cnt - i)    
t1 = time.time() - t1

times.append(t1)

t2 = time.time()
for j in range(5):
    for i in range(3):
        g1.app_nodes[cnt - i].app_proc_send_to("SIMPLE", i, "latency test", None, cnt - i)

t2 = time.time() - t2     
times.append(t2)   
    
t3 = time.time()
for j in range(5):
    for i in range(3):
        g1.app_nodes[cnt - i].app_proc_send_to("SIMPLE", i, "latency test", None, cnt - i)
        time.sleep(0.2)

t3 = time.time() - t3
times.append(t3)

print(t1, " - ", t2, " - ", t3)

print("tempo: ", t1)
input("PRESS ENTER TO CONTINUE")

import matplotlib.pyplot as plt

# Valori da plottare
labels = ['No Delay', 'Delay = 0.1s', 'Delay = 0.2s', 'Avg0', 'Avg1', 'Avg2']
avgs = [t1 / 15, (t2 - 15*0.1) / 15, (t3 - 15*0.2)/15]
idx = 0
to_print = []

for elem in times:
    to_print.append(elem)

for elem in avgs:
    to_print.append(elem)

# Creazione del grafico a barre
plt.figure(figsize=(8, 6))
plt.bar(labels, to_print)

# Aggiunta delle etichette e del titolo
plt.ylabel('Time')
plt.title('Tests')

# Mostra il grafico
plt.show()


# try:
#     with open("./rsm_check_faulty_times.txt", 'a') as file:
#         file.write(f"5, 1 : {t1}")
#         print("Time added to txt")
# except Exception as e:
#     print(f"Error while file writing: {e}")


g1.stop_event.set()
g1.cleanup()

input("PRESS ENTER TO CONTINUE")
