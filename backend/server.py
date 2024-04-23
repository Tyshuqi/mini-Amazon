import threading
from mysocket import *
from handleWorld import *
from handleUPS import *

from ack import *
from protocal import web_backend_pb2 as web
from protocal import world_amazon_pb2 as world
from protocal import amazon_ups_pb2 as ups
from connectdb import get_db_connection
from ack import ack_list
from handleWeb import *



def world_thread(world_fd, ups_fd):
    print("World thread is running")
    try:
        connect(world_fd)
        world_id = rec_connected(world_fd)
        #world_id = 789
        print(f"Recieve World ID: {world_id}")
        initIventory(world_fd)

        while True:
            res = receiveResponse(world_fd, world.AResponses)
            print("Recved from world!")
            
            # remove ack from ack_list
            for ack in res.acks:
                ack_list.remove_ack(ack)
            
            for ready in res.ready:
                print("Recved ready packed from world!")
                sendAck_world(world_fd, ready.seqnum)
                # update order statuse to "packed"
                packed(world_fd, ready.shipid)
                
            for err in res.error:
               print(f"Error from world: {err.err}, Origin SeqNum: {err.originseqnum}")
               sendAck_world(world_fd, err.seqnum)
                
            for loaded_row in res.loaded:
                print("Recved loaded from world!")
                sendAck_world(world_fd, loaded_row.seqnum)
                # TODO 5: write loaded in handleWorld, just update order_status? has finished this!
                loaded(world_fd, loaded_row.shipid) 
                # TODO 6: send startDelivery to ups, has finished this!
                startDelivery(ups_fd, loaded_row.shipid)
            
            for arrived in res.arrived:
                print("Recved arrived from world!")
                sendAck_world(world_fd, arrived.seqnum)  
                # TODO 3: write arrived in handleWorld, just update dabase, has finished this!
                for item in arrived.things:
                    purchase_more_arrived(item.id, item.count)
             
                
    except Exception as e:
        print(f"Error in world thread: {e}")


def ups_thread(ups_fd, world_fd):
    try:
        print("ups thread is running")

        while True:
            res = receiveResponse(ups_fd, ups.UCommand)
            
            # remove ack from ack_list
            for ack in res.acks:
                ack_list.remove_ack(ack)
                
            # 4.22
            for check_User in res.checkUser:
                print("Recved checkUser from ups!")
                sendAck_ups(ups_fd, check_user.seqnum)
                # uodate order status and upsid, check upsid!=-1 continue, else change status
                ups_id = check_User.upsUserID
                if ups_id != -1:
                    # update ups id
                    updateUpsID(ups_id, check_User.orderid)
                    
                    toPack(world_fd, buy.orderid)
                    # TODO 2: request truck from ups, has finished this!
                    toOrderTruck(ups_fd, buy.orderid)
                else:
                    # update order status to "error"
                    updateOrderStatus(check_User.orderid, "error")
                    
                             
            for arrive in res.arrived:
                print("Recved truck arrived from ups!")
                sendAck_ups(ups_fd, arrive.seqnum)
                # TODO 4: wait for order.status== packed,  start load, send to world
                orderID = arrive.packageID
                while True:
                    try:
                        if getOrderStatus(orderID) == "packed":
                            print("Order is packed and ready for loading.")
                            break
                    except Exception as e:
                        print(f"Error checking order status: {e}")
                    # Wait before checking the status again to reduce load on the database
                    time.sleep(2)    
                toLoad(world_fd, orderID, arrive.truckID)
 
            for delivered_row in res.delivered:
                print("Recved delivered from ups!")
                sendAck_ups(ups_fd, delivered_row.seqnum)
                # TODO 7: just update order status?  has finished this!
                delivered(ups_fd, delivered_row.packageID)
                
            for err in res.error:
                print(f"Error from ups: {err.err}, Origin SeqNum: {err.originseqnum}")
                sendAck_ups(ups_fd, err.seqnum)
            
    except Exception as e:
        print(f"Error in UPS thread: {e}")


def webapp_thread(webapp_fd, world_fd, ups_fd):
    try:
        print("Webapp thread is running")
        
        while True:
            res = receiveResponse(webapp_fd, web.WCommands) 
            print("Recved from webapp!")
            
            for buy in res.buy:
                print("Recved user buy sth from webapp!")
                sendAck_web(webapp_fd, buy.seqnum)
                # 4.22 check upsname
                Name = checkName(buy.orderid)
                # None: pack directly, else send to ups
                if Name == None:
                    toPack(world_fd, buy.orderid)
                    # TODO 2: request truck from ups, has finished this!
                    toOrderTruck(ups_fd, buy.orderid)
                else:
                    #send to ups
                    sendName(ups_fd, Name) 

                
            for askmore in res.askmore:
                print("Recved askmore from webapp!")
                print("Handling webapp Waskmore!")
                #sendAck_web(webapp_fd, askmore.seqnum)
                # TODO 1: has finished this
                toPurchaseMore(world_fd, askmore.productid, askmore.count)
        
    except Exception as e:
        print(f"Error in webapp thread: {e}")



if __name__ == "__main__":
    print("Amazon Server is running")
    # Socket setup
    #worldFD = clientSocket('vcm-38127.vm.duke.edu', 23456)
    worldFD = clientSocket('vcm-38181.vm.duke.edu', 23456)
    print("Success connect to worldFD:", worldFD)
    
    # server_fd2 = serverSocket('vcm-38181.vm.duke.edu', 34567)
    # upsFD, addr2 = server_fd2.accept()
    # print("Success connect to ups:", upsFD)
    upsFD = 5
    
    server_fd = serverSocket('vcm-38181.vm.duke.edu', 45678)
    webappFD, addr = server_fd.accept()
    webappFD, addr = server_fd.accept()
    webappFD, addr = server_fd.accept()
    print("Success connect to webappFD:", webappFD)
    #webappFD = 6
    
    #ack_list = AckTracker()

    # Thread initiation
    world_thread = threading.Thread(target=world_thread, args=(worldFD, upsFD))
    ups_thread = threading.Thread(target=ups_thread, args=(upsFD,worldFD))
    webapp_thread = threading.Thread(target=webapp_thread, args=(webappFD,worldFD, upsFD))

    # Start threads
    world_thread.start()
    ups_thread.start()
    webapp_thread.start()

    # Join threads to ensure they complete
    world_thread.join()
    ups_thread.join()
    webapp_thread.join()
