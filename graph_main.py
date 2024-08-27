from graph_gen import Graph
import sys
# import pyautogui
import time

#
#                                                       | send source dest msg
# expected syntax: python/python3 graph_main.py #nodes -| bc source msg
#                                                       | ...
#

g = None

l = len(sys.argv)

match l:
    case 3:
        match sys.argv[2]:
            case 'test':
                g = Graph(int(sys.argv[1]), 0.3)
                g.specialBC(int(int(sys.argv[1]) / 2), 'test')
                input("")
                print("\n")
                g.pfd_test(int(0))
                input("")
                print("\n")
                g.specialBC(int(0), 'test')
    case 4:
        match sys.argv[2]:
            case 'pfd':
                g = Graph(int(sys.argv[1]), None)
                g.plot_graph()
                g.pfd_test(int(sys.argv[3]))
                
                # input("")
                
                # for node in g.nodes.values():
                #     node.cleanup()
        
    case 5:
        cmd = sys.argv[2]
        match cmd:
            case 'bc':
                g = Graph(int(sys.argv[1]), None)
                g.plot_graph()
                g.BC_send(int(sys.argv[3]), sys.argv[4])
                
                # input("")
                
                # for node in g.nodes.values():
                #     node.cleanup()
            
            case 'special_bc':
                g = Graph(int(sys.argv[1]), None)
                g.plot_graph()
                g.specialBC(int(sys.argv[3]), sys.argv[4])
                
                # input("")
                
                # for node in g.nodes.values():
                #     node.cleanup()
            case 'consensus':
                g = Graph(int(sys.argv[1]), None)
                g.plot_graph()
                g.ask_consensus(int(sys.argv[3]), sys.argv[4])
                input("")
                g.print_agreed_values()
                
                
    case 6:
        cmd = sys.argv[2]
        match cmd:
            case 'send':
                g = Graph(int(sys.argv[1]), None)
                g.plot_graph()
                
                print("shortest path:", g.shortPath(int(sys.argv[3]), int(sys.argv[4])) )
                g.send_msg(int(sys.argv[3]), int(sys.argv[4]), str(sys.argv[5]))
                
                # input("")
                
                # for node in g.nodes.values():
                #     node.cleanup()
            case 'send_no_path':
                g = Graph(int(sys.argv[1]), None)
                g.plot_graph()
                
                print("shortest path:", g.shortPath(int(sys.argv[3]), int(sys.argv[4])) )
                g.send_msg(int(sys.argv[3]), int(sys.argv[4]), str(sys.argv[5]))
                
                # input("")
                
                # for node in g.nodes.values():
                #     node.cleanup()
input("")

g.stop_event.set()
                
for node in g.nodes.values():
    node.cleanup()
    
"""
if(len(sys.argv) == 5):
    cmd = str(sys.argv[2])
    if(str(sys.argv[2]) == "term"):
        g = Graph(int(sys.argv[1]), "term")
        g.plot_graph()
        g.shortPath()
    elif(str(sys.argv[2]) == "noterm"):
        g = Graph(int(sys.argv[1]), None)
        print(g.shortPath(int(sys.argv[3]), int(sys.argv[4])) ) 
        g.plot_graph()
        
elif(len(sys.argv) == 6):
    g = Graph(int(sys.argv[1]), None)
    print(g.shortPath(int(sys.argv[3]), int(sys.argv[4])) ) 
    # g.send_msg(int(sys.argv[3]), int(sys.argv[4]), str(sys.argv[5]))

    g.plot_graph()
    g.first_BC_send()

    input("")
    #time.sleep(1)
    #pyautogui.press('enter') #TODO Asseggnarlo ad un altro thread
    
    # g.get_matrix_clock()
    # g.get_message_logs()
    
    for node in g.nodes.values():
        node.cleanup()
    
            
elif(len(sys.argv) == 2):
    g = Graph(int(sys.argv[1]), None)
    g.plot_graph()
    g.shortPath()

else:
    print("Invalid input")
"""