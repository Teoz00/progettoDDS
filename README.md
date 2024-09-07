# progettoDDS
Detecting Causality in the Presence of Byzantine Processes

#TODO
#1 Consensus -> done (with flooding, usage of commander-lieutants algorithm suggested by Leslie Lamport)
#2 bc (for consensous) -> done (flooding)
#3 ack (priority) ==> send msg s.t. I'm Alive / nack
#4 pfd (to see) -> done
#5 agreement:  Every non-faulty replica receives every message. -> done (hopefully)
#6 FIFO
#7 LASKALSJ : This matrix is used to track and order events across different processes in such a system.
#8 RSM (replication set machine) ==> implied such module RSM.py (class with finite state + FIFO + agreememt)

###IDEA: macro-nodes containing graph of RSMs, each of them receives a set of events coming from macro-node (above level) and elaborates it,
###consensus between RSMs, macro-nodes communicate also something an RSM may decide to send out the ensemble if consensus is reached(macro-node)

    -------------------------
    |   APPLICATION GRAPH   |
    -------------------------
        ^           |
        |           ˇ
    -------------------------
    |  APPLICATION PROCESS  |
    -------------------------
        ^           |
        |           ˇ
    -------------------------
    |       GRAPH           |
    -------------------------
        ^           |
        |           ˇ
    -------------------------
    |       GRAPH NODE      |  ----------
    -------------------------   <-----| |
      ^   |   ^   |    ^  |           | |
      |   ˇ   |   ˇ    |  ˇ           | |
    -------- -------  -------         | |
    | CONS | | RSM |  | PFD |         | |
    -------- -------  -------         | |
      ^ |      ^ |      ^ |           | |
      | ˇ      | ˇ      | ˇ           | |
    -------------------------         | |
    |         PP2P          |   ------- |
    -------------------------   <--------

###OPTIONAL: review graph init assigning of tcp ports for nodes connections since there might be some issues 

###COMMANDS
#git branch
#git checkout "nome_branch"
#git branch 
#git add . -> git commit -m "msg(con virgolette)" -> git push origin "nome branch"
#git pull origin "nome branch"