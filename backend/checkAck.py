from server import ack_list
from mysocket import *
import world_amazon_pb2 as world
import web_backend_pb2 as web
import amazon_ups_pb2 as ups
import time


# send request until receive ack
def checkAndSendReq(fd, req_msg, seqNum ):
    while True:
        # check ack in seq_list: resend
        if seqNum in ack_list.pending_acks:
            sendRequest(fd, req_msg)
            time.sleep(2)  # waits for 2 seconds
        # otherwise break
        else:
            break
        
def sendAck_world(fd, seqNum):
    ack_msg = world.ACommands()
    ack_msg.acks = seqNum
    sendRequest(fd, ack_msg)
    
def sendAck_web(fd, seqNum):
    ack_msg = web.BResponse()
    ack_msg.acks = seqNum
    sendRequest(fd, ack_msg)
    
def sendAck_ups(fd, seqNum):
    ack_msg = ups.ACommand()
    ack_msg.acks = seqNum
    sendRequest(fd, ack_msg)