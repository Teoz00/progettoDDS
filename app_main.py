from app_graph import ApplicationGraph

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


sys.setrecursionlimit(2147483647) # max int C as parameter
g = ApplicationGraph(int(sys.argv[1]), int(sys.argv[2]))

# g.plot_graph()

# TEST FOR GIVING INPUT TO RSM
# g.app_nodes[0].subgraph.nodes[0].recv_input_rsm(g.app_nodes[0].subgraph.nodes[0].generate_event_set("[['SEND', '0', 'msg1'], ['RECV', '2', 'msg1']]"))

# TEST FOR DETECTING FAULTY APP PROCESSES
# g.check_faulty_procs()
# input("")

# TEST FOR CHECKING PFD AMONG RSMS
g.check_faulty_rsms()
input("")

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
g.app_nodes[0].app_proc_send_to("SIMPLE", 2, "ciao", None, 0)
time.sleep(1.0)
g.app_nodes[2].app_proc_send_to("SIMPLE", 0, "ciao", None, 2)
time.sleep(1.0)
g.app_nodes[2].app_proc_send_to("SIMPLE", 1, "ciao", None, 2)
time.sleep(1.0)
g.app_nodes[1].app_proc_send_to("SIMPLE", 0, "ciao", None, 1)
time.sleep(1.0)

input("")

# 0 -> 2, 2 -> 0, 2 -> 1, 1 -> 0

# TEST FOR ACHIEVING CONSENSUS FOR RSMS
g.get_consensus_rsms_processes(0, g.app_nodes[0].subgraph.nodes[0].rsm.V.matrix)
input("")

print("V0 - ", end = "")
g.app_nodes[0].V.print_matrix()
print("V1 - ", end = "")
g.app_nodes[1].V.print_matrix()
print("V2 - ", end = "")
g.app_nodes[2].V.print_matrix()

# processo 0, processo 2
# evento 0,     evento 1
print("Testing causality : ", g.test_causality(0, 2, 1, 1))


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

if(len(sys.argv) == 4):
    if(sys.argv[3] == "clean"):
        directory_cleaner()