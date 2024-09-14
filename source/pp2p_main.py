from pp2p import PerfectPointToPointLink
import sys

if len(sys.argv) != 3:
    print("There are some issues with user input")
    sys.exit(1)
    
this_address = sys.argv[1]
peer_address = sys.argv[2]

pl = PerfectPointToPointLink(this_address, peer_address)
pl.print_info()

messageLog = []
try:
    while True:
        msg = input("Insert message to send: ")
        if(msg != None and msg != 'exit' and msg != ''):
            messageLog.append(msg)
        if(msg):
            
            pl.send(msg)
            print("Sent: ", msg)
            
            if(msg == "exit"):
                print(messageLog)
                break
            
        msg = pl.recv()
        if(msg != None and msg != 'exit' and msg != ''):
            messageLog.append(msg)
        if(msg == "exit"):
            break
 
except:
    print("Interrupted by user")

# to run the code open two windows of terminal where you have to write the following commands:
#    1st terminal: python3 pp2p_main.py 127.0.0.1:5555 127.0.0.1:5556
#    2nd terminal: python3 pp2p_main.py 127.0.0.1:5556 127.0.0.1:5555

""" NOTES:
    - free ports -> 49152 : 65535
"""