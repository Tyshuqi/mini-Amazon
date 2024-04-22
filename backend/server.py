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

def world_thread(world_fd, ups_fd):
    print("World thread is running")
    try:
        connect(world_fd)
        world_id = rec_connected(world_fd)
        print(f"Recieve World ID: {world_id}")
        while True:
            res = receiveResponse(world_fd, world.AResponses)
            print("Recved from world!")
            
            # remove ack from ack_list
            for ack in res.acks:
                ack_list.remove_ack(ack)
            
            for ready in res.ready:
                sendAck_world(world_fd, ready.seqnum)
                # update order statuse to "packed"
                packed(world_fd, ready.shipid)
                
            for err in res.error:
               print(f"Error from world: {err.err}, Origin SeqNum: {err.originseqnum}")
                
            for loaded_row in res.loaded:
                sendAck_world(world_fd, loaded_row.seqnum)
                # TODO 5: write loaded in handleWorld, just update order_status? has finished this!
                loaded(world_fd, loaded_row.shipid) 
                # TODO 6: send startDelivery to ups, has finished this!
                startDelivery(ups_fd, loaded_row.shipid)
            
            for arrived in res.arrived:
                sendAck_world(world_fd, arrived.seqnum)  
                # TODO 3: write arrived in handleWorld, just update dabase, has finished this!
                purchase_more_arrived(arrived.things.productid, arrived.things.count)
             
                
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
             
            for arrive in res.arrived:
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
                sendAck_ups(ups_fd, delivered_row.seqnum)
                # TODO 7: just update order status?  has finished this!
                delivered(ups_fd, delivered_row.packageID)
                
            for err in res.error:
                print(f"Error from ups: {err.err}, Origin SeqNum: {err.originseqnum}")
            
    except Exception as e:
        print(f"Error in UPS thread: {e}")


def webapp_thread(webapp_fd, world_fd, ups_fd):
    try:
        print("Webapp thread is running")
        
        while True:
            res = receiveResponse(webapp_fd, web.WCommands) 
            print("Recved from webapp!")
            
            for buy in res.buy:
                print("Handling webapp Wbuy!")
                #sendAck_web(webapp_fd, buy.seqnum)
                toPack(world_fd, buy.orderid)
                # TODO 2: request truck from ups, has finished this!
                toOrderTruck(ups_fd, buy.orderid)
                
                
            # for cancel in res.cancel:
            #     pass
                
            for askmore in res.askmore:
                print("Handling webapp Waskmore!")
                #sendAck_web(webapp_fd, askmore.seqnum)
                # TODO 1: has finished this
                toPurchaseMore(world_fd, askmore.productid, askmore.amount)
        
    except Exception as e:
        print(f"Error in webapp thread: {e}")


def getOrderStatus(order_id):
    conn = get_db_connection()
    if conn is None:
        print("Database connection failed")
        return None
    
    with conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT status FROM Order WHERE id = %s", (order_id,))
            result = cursor.fetchone()
            return result[0] if result else None



if __name__ == "__main__":
    print("Amazon Server is running")
    # Socket setup
    #worldFD = clientSocket('vcm-38127.vm.duke.edu', 23456)
    worldFD = clientSocket('vcm-38181.vm.duke.edu', 23456)
    print("Success connect to worldFD:", worldFD)
    #upsFD = clientSocket("vcm-40471.vm.duke.edu", 34567)
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
