from mysocket import *
from handleWorld import *
from ack import *



if __name__ == "__main__": 
    # build socket
    world_fd = clientSocket("vcm-38127.vm.duke.edu", 23456)
    ups_fd = clientSocket("vcm-", 34567)
    webapp_fd = serverSocket("0.0.0.0", 45678)
    
    
    connect(world_fd)
    world_id = rec_connected(world_fd)

    ack_list = AckTracker()
    