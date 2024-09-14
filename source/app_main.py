from app_graph import ApplicationGraph

import matplotlib.pyplot as plt
import sys
import time
import os

def directory_cleaner():
    dir_path = "./txt_files"
    
    try:
        dir = os.listdir(dir_path)
        print(f"Removing {len(dir)} elements... ", end="")
        
        for file in dir:
            path = os.path.join(dir_path, file)

            if os.path.isfile(path):
                os.remove(path)
        
        print("done!")

    except OSError:
        print("\nError while cleaning 'txt_files' directory")

times = {}

sys.setrecursionlimit(2147483647) # max int C as parameter
t = time.time()
g = ApplicationGraph(int(sys.argv[1]), int(sys.argv[2]))
t = time.time() - t
times.update({"Initialization" : t})
# g.plot_graph()

# TEST FOR GIVING INPUT TO RSM
# g.app_nodes[0].subgraph.nodes[0].recv_input_rsm(g.app_nodes[0].subgraph.nodes[0].generate_event_set("[['SEND', '0', 'msg1'], ['RECV', '2', 'msg1']]"))

# TEST FOR DETECTING FAULTY APP PROCESSES
# g.check_faulty_procs()
# input("")

# TEST FOR CHECKING PFD AMONG RSMS
t = time.time()
g.check_faulty_rsms()
t = time.time() - t
input("PRESS ENTER TO CONTINUE")
times.update({"RSMs faulty check" : t})
input("PRESS ENTER TO CONTINUE")


# TEST FOR DETECING FAULTY APPLICATION PROCESSES (deprecated)
# g.app_nodes[0].app_proc_pfd_caller()
# input("")

# TEST FOR ACHIEVING CONSENSUS FROM A *RANDOM* APPLICATION PROCESS
# g.ask_consensus_app_procs("helo")
# input("")

# TEST FOR ACHIEVING CONSENSUS FOR *ALL* APPLICATION PROCESSES
# g.app_nodes[0].app_ask_consensus_commander(None, "v4lu3")
# input("")

# TEST FOR SENDING MESSAGES AMONG APPLICATION PROCESSES
t = time.time()
g.app_nodes[0].app_proc_send_to("SIMPLE", 2, "ciao", None, 0)
t = time.time() - t
times.update({"0 sends to 2" : t})
time.sleep(1.0)

t = time.time()
g.app_nodes[2].app_proc_send_to("SIMPLE", 0, "ciao", None, 2)
t = time.time() - t
times.update({"2 sends to 0" : t})
time.sleep(1.0)

t = time.time()
g.app_nodes[2].app_proc_send_to("SIMPLE", 1, "ciao", None, 2)
t = time.time() - t
times.update({"2 sends to 1" : t})
time.sleep(1.0)

t = time.time()
g.app_nodes[1].app_proc_send_to("SIMPLE", 0, "ciao", None, 1)
t = time.time() - t
times.update({"1 sends to 0" : t})
time.sleep(1.0)

input("PRESS ENTER TO CONTINUE")

# 0 -> 2, 2 -> 0, 2 -> 1, 1 -> 0

# TEST FOR ACHIEVING CONSENSUS FOR RSMS

# get_consensus_rsms_processes needs the id of the process, the id of the rsm and what they need to agree
t = time.time()
if(g.get_consensus_single_proc(0, 0, g.app_nodes[0].subgraph.nodes[0].rsm.V.matrix)):
    t = time.time() - t
    times.update({"Consensus RSM(0,0)" : t})
    input("PRESS ENTER TO CONTINUE")
    t = time.time()
    if(g.get_consensus_single_proc(2, 1, g.app_nodes[2].subgraph.nodes[1].rsm.V.matrix)):
        t = time.time() -t
        times.update({"Consensus RMS(2,1)" : t})
        input("PRESS ENTER TO CONTINUE")

        print("V0 - ", end = "")
        g.app_nodes[0].V.print_matrix()
        print("V1 - ", end = "")
        g.app_nodes[1].V.print_matrix()
        print("V2 - ", end = "")
        g.app_nodes[2].V.print_matrix()

        # processo 0, processo 2
        # evento 0,     evento 1
        t = time.time()
        print("Testing causality : ", g.test_causality(0, 2, 1, 1))
        t = time.time() - t
        times.update({"Causality check 1" : t})

        input("PRESS ENTER TO CONTINUE")

        
t = time.time()
if(g.get_consensus_single_proc(1, 3, g.app_nodes[1].subgraph.nodes[3].rsm.V.matrix)):
    t = time.time() - t
    times.update({"Consensus RSM(1,3)" : t})
    input("PRESS ENTER TO CONTINUE")
    t = time.time()
    if(g.get_consensus_single_proc(2, 1, g.app_nodes[2].subgraph.nodes[1].rsm.V.matrix)):
        t = time.time() -t
        times.update({"Consensus RMS(2,1)" : t})
        input("PRESS ENTER TO CONTINUE")

        print("V0 - ", end = "")
        g.app_nodes[0].V.print_matrix()
        print("V1 - ", end = "")
        g.app_nodes[1].V.print_matrix()
        print("V2 - ", end = "")
        g.app_nodes[2].V.print_matrix()
        
        t = time.time()
        print("Testing causality : ", g.test_causality(1, 2, 2, 1))
        t = time.time() - t
        times.update({"Causality check 2" : t})
        
        
        input("PRESS ENTER TO CONTINUE")
        print("times : ", times)

# g.get_consensus_rsms_processes(0, g.app_nodes[0].subgraph.nodes[0].rsm.V.matrix)
# input("")

# print("V0 - ", end = "")
# g.app_nodes[0].V.print_matrix()
# print("V1 - ", end = "")
# g.app_nodes[1].V.print_matrix()
# print("V2 - ", end = "")
# g.app_nodes[2].V.print_matrix()

# g.app_nodes[0].subgraph.nodes[0].rsm.printAllEvents()

# type, peer_id, msg, msg_id, origin

# TEST FOR SETTING RSM INPUT EVENTS
# g.eventGenerator("SEND", 1, 0, "firstTest")
# g.eventGenerator("SEND", 2, 3, "firstTest")
# g.eventGenerator("SEND", 0, 1, "firstTest")
# g.eventGenerator("SEND", 1, 2, "firstTest")

# g.app_rsm_recver(g.happened_events)

# for elem in g.app_nodes:
#     print(f"{g.app_nodes[elem]} > ")
#     # g.app_nodes[elem].print_cons()
#     print()

g.stop_event.set()
g.cleanup()
labels = list(times.keys())
sizes = list(times.values())

plt.barh(labels, sizes, color='#039dfc')
plt.xlabel('Time (s)')
plt.ylabel('Phases')
plt.title('Execution time distribution')

plt.tight_layout()
plt.show()

for index, value in enumerate(sizes):
    plt.text(value, index, f'{value:.6f}', va='center', ha='left', color='black')

if(len(sys.argv) == 4):
    if(sys.argv[3] == "clean"):
        directory_cleaner()