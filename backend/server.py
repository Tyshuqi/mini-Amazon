import threading
from mysocket import *
from handleWorld import *
from ack import *
import web_backend_pb2 as web

def world_thread(world_fd, ack_list):
    try:
        connect(world_fd)
        world_id = rec_connected(world_fd)
        print(f"Connected to World with ID: {world_id}")
        # Further processing and world interaction
        while True:
            # Receive message from world
            res = receiveResponse(world_fd, world.AResponses)
            
            # remove ack from ack_list
            for ack in res.acks:
                ack_list.remove_ack(ack)
            
            # if ready not null
            for ready in res.ready:
                sendAck_world(world_fd, ready.seqnum)
                packed(world_fd, ready.shipid, ready.seqnum)
                
            for err in res.error:
                # TODO: handle error
                print(f"Error from world: {err.msg}")
                
            for loaded in res.loaded:
                # TODO: write loaded in handleWorld
                
                # TODO: send startDelivery to ups
                
                
             
                
    except Exception as e:
        print(f"Error in world thread: {e}")


def ups_thread(ups_fd):
    try:
        connect(ups_fd)
        print("Connected to UPS server")
        # Further UPS communication
        
        while True:
            res = receiveResponse(ups_fd, ups.UCommand)
            
            # remove ack from ack_list
            for ack in res.acks:
                ack_list.remove_ack(ack)
             
            for arrive in res.arrived:
                sendAck_ups(ups_fd, arrive.seqnum)
                # TODO: start load, send to world
                toLoad(world_fd, arrive.shipid)
                
            for deliver in res.delivered:
                sendAck_ups(ups_fd, deliver.seqnum)
                # TODO: update order status
                
            for err in res.error:
                # TODO: handle error
                print(f"Error from world: {err.msg}")
            
                
            
    except Exception as e:
        print(f"Error in UPS thread: {e}")


def webapp_thread(webapp_fd, world_fd, ups_fd):
    try:
        print("Webapp server is running")
        
        while True:
            res = receiveResponse(webapp_fd, web.Wcommands) 
            
            for buy in res.Wbuy:
                sendAck_web(webapp_fd, buy.seqnum)
                toPack(world_fd, buy.orderid)
                # TODO request truck from ups
                
                
            for cancel in res.cancel:
                
            for askmore in res.Waskmore:
                sendAck_web(webapp_fd, askmore.seqnum)
                toPurchaseMore(world_fd, askmore.productid, askmore.amount)
        
    except Exception as e:
        print(f"Error in webapp thread: {e}")




if __name__ == "__main__":
    # Socket setup
    world_fd = clientSocket("vcm-38127.vm.duke.edu", 23456)
    ups_fd = clientSocket("vcm-", 34567)
    webapp_fd = serverSocket("0.0.0.0", 45678)
    
    ack_list = AckTracker()

    # Thread initiation
    world_thread = threading.Thread(target=world_thread, args=(world_fd, ack_list))
    ups_thread = threading.Thread(target=ups_thread, args=(ups_fd,))
    webapp_thread = threading.Thread(target=webapp_thread, args=(webapp_fd,))

    # Start threads
    world_thread.start()
    ups_thread.start()
    webapp_thread.start()

    # Join threads to ensure they complete
    world_thread.join()
    ups_thread.join()
    webapp_thread.join()
