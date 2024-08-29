from app_graph import ApplicationGraph

import sys

g = ApplicationGraph(int(sys.argv[1]), int(sys.argv[2]))
g.plot_graph()

input("")

g.stop_event.set()
g.cleanup()