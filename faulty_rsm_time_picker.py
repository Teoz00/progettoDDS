from app_graph import ApplicationGraph
import matplotlib.pyplot as plt
import time

case_1 = [5, 2]

g1 = ApplicationGraph(case_1[0], case_1[1])
t1 = time.time()
g1.check_faulty_rsms()
t1 = time.time() - t1

print("tempo: ", t1)
input("PRESS ENTER TO CONTINUE")

try:
    with open("./rsm_check_faulty_times.txt", 'a') as file:
        file.write(f"5, 1 : {t1}")
        print("Time added to txt")
except Exception as e:
    print(f"Error while file writing: {e}")


g1.stop_event.set()
g1.cleanup()

input("PRESS ENTER TO CONTINUE")
