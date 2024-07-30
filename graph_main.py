from graph_gen import Graph
import sys
import pyautogui
import time

# expected syntax: python graph_main.py <# nodes> <"term" or nothing>
g = None

if(len(sys.argv) == 5):
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
    g.send_msg(int(sys.argv[3]), int(sys.argv[4]), str(sys.argv[5]))
    # g.plot_graph()

    input("")
    #time.sleep(1)
    #pyautogui.press('enter') #TODO Asseggnarlo ad un altro thread
    
    for node in g.nodes.values():
        node.cleanup()
            
elif(len(sys.argv) == 2):
    g = Graph(int(sys.argv[1]), None)
    g.plot_graph()
    g.shortPath()

else:
    print("Invalid input")