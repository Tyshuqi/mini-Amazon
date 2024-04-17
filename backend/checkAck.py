from server import ack_list
from mysocket import *

def checkAndSend(fd, req_type, seqNum ):
    while True:
        # check ack in seq_list: resend
        if seqNum in ack_list.pending_acks:
            sendRequest(fd, req_type)
        # otherwise break
        else:
            break