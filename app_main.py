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
g.app_nodes[0].subgraph.nodes[0].recv_input_rsm(g.app_nodes[0].subgraph.nodes[0].generate_event_set("[['SEND', '0', 'msg1'], ['RECV', '2', 'msg1']]"))

# g.check_faulties()
# input("")
# g.get_consensus_processes(0, 'test4consensus')
# input("")
# g.app_nodes[0].app_proc_broadcast("First broacast!")
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