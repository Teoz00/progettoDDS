from graph_gen import Graph
import sys

# expected syntax: python graph_main.py <# nodes> <"term" or nothing>
g = None

if(len(sys.argv) == 3):
    if(str(sys.argv[2]) == "term"):
        g = Graph(int(sys.argv[1]), "term")
        g.plot_graph()
    elif(str(sys.argv[2]) == "noterm"):
        g = Graph(int(sys.argv[1]), None)
        g.plot_graph()

elif(len(sys.argv) == 2):
    g = Graph(int(sys.argv[1]), None)
    g.plot_graph()

else:
    print("Invalid input")