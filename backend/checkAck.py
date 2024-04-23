from ack import ack_list
from mysocket import *
from protocal import world_amazon_pb2 as world
from protocal import web_backend_pb2 as web
from protocal import amazon_ups_pb2 as ups
import time


# send request until receive ack
def checkAndSendReq(fd, req_msg, seqNum ):
    print("seqNum: ", seqNum)
    while True:
        # check ack in seq_list: resend
        print("pending set: ",ack_list.pending_acks)
        if seqNum in ack_list.pending_acks:
            print("still in list" )
            sendRequest(fd, req_msg)
            time.sleep(2)  # waits for 2 seconds
        # otherwise break
        else:
            print("break")
            break
        
def sendAck_world(fd, seqNum):
    req_msg = world.ACommands()
    req_msg.acks.append(seqNum)
    sendRequest(fd, req_msg)
    
def sendAck_web(fd, seqNum):
    req_msg = web.BResponse()
    req_msg.acks.append(seqNum)
    sendRequest(fd, req_msg)
    
def sendAck_ups(fd, seqNum):
    req_msg = ups.ACommand()
    req_msg.acks.append(seqNum)
    sendRequest(fd, req_msg)