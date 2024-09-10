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

# TEST FOR CHECKING PFD AMONG RSMS
# g.check_faulty_rsms()
# input("")

# TEST FOR DETECTING FAULTY APP PROCESSES
g.check_faulty_procs()
input("")

# TEST FOR DETECING FAULTY APPLICATION PROCESSES
# g.app_nodes[0].app_proc_pfd_caller()
# input("")

# TEST FOR ACHIEVING CONSENSUS FOR RSMS
# g.get_consensus_rsms_processes(0, 'test4consensus')
# input("")

# TEST FOR ACHIEVING CONSENSUS FROM A *SPECIFIC* APPLICATION PROCESS
# g.ask_consensus_app_procs("helo")
# input("")

# TEST FOR ACHIEVING CONSENSUS FOR *ALL* APPLICATION PROCESSES
# g.app_nodes[0].app_ask_consensus_commander(None, "v4lu3")
# input("")

# for elem in g.app_nodes:
#     print(f"{g.app_nodes[elem]} > ")
#     # g.app_nodes[elem].print_cons()
#     print()

g.stop_event.set()
g.cleanup()

if(len(sys.argv) == 4):
    if(sys.argv[3] == "clean"):
        directory_cleaner()