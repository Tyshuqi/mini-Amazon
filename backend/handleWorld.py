import psycopg2
import world_amazon_pb2 as world
from mysocket import *
from server import ack_list
from checkAck import *


def connect(fd):
    # connect to db
    conn = psycopg2.connect(
        dbname="database_name",
        user="username",
        password="password",
        host="localhost",
        port="5432"  # default PostgreSQL port
    )
    
    # Create a cursor object
    cursor = conn.cursor()
    # select warehouse info
    cursor.execute('SELECT id, x, y  FROM Warehouse')
    # Fetch data
    all_warehouse = cursor.fetchall()
    
    # init world
    connect_msg = world.AConnect()
    connect_msg.isAmazon = True
    
    for warehouse in all_warehouse:
        new_wh = connect_msg.initwh.add()
        new_wh.id = warehouse[0]
        new_wh.x = warehouse[1]
        new_wh.y = warehouse[2]
    # send Aconnect to world     
    sendRequest(fd, connect_msg)
        
    cursor.close()
    conn.close()
    
    
    
def rec_connected(fd):
    res = receiveResponse(fd, AConnected)
    if res.result == 'connected!':
        world_id = res.world_id
        return world_id
    else:
        print(f"Failed to connect: {res.result}")
        sys.exit(1)  
        
        
    

def toPack(fd, orderID):
    
    # connect to db
    conn = psycopg2.connect(
        dbname="database_name",
        user="username",
        password="password",
        host="localhost",
        port="5432"  # default PostgreSQL port
    )
    cursor = conn.cursor()
    # select warehouse info
    cursor.execute('SELECT product_id, description, count FROM Product, Order WHERE Product.id = Order.productID AND Order.id = orderID')
    all_product = cursor.fetchall()
    
    # message APack:whnum, things, shipid, seqnum
    pack_msg = world.APack()
    for product in all_product:
        newproduct = pack_msg.things.add()
        newproduct.id = product[0]
        newproduct.description = product[1]
        newproduct.count = product[2]
    # get whnum 
    cursor.execute('SELECT whnum FROM Order WHERE Order.id = orderID')
    #warehouseNum = cursor.fetchall()
    warehouseNum = cursor.fetchone()[0]
    pack_msg.whnum = warehouseNum
    # get shipid
    pack_msg.shipid = orderID
    # generate a seq_num
    seqNum = ack_list.add_request()
    pack_msg.seqnum = seqNum
    # send APack until receive ack    
    checkAndSendReq(fd, pack_msg, seqNum)
    
    # update order status 
    update_query = "UPDATE Order SET status = %s WHERE id = %s"
    cursor.execute(update_query, ('packing', orderID))
    conn.commit()
    # clean up
    cursor.close()
    conn.close()
    

def packed(fd, orderid, seqnum):
    # connect to db
    conn = psycopg2.connect(
        dbname="database_name",
        user="username",
        password="password",
        host="localhost",
        port="5432"  # default PostgreSQL port
    )
    cursor = conn.cursor()

    # Get order details including the product and warehouse information
    cursor.execute("""
    SELECT Order.quantity, Product.id, Product.quantity as product_stock
    FROM Order
    JOIN Product ON Product.product_id = Order.product_id
    WHERE Order.id = %s""", (orderid,))
    order_details = cursor.fetchone()

    if order_details:
        ordered_quantity = order_details[0]
        product_id = order_details[1]
        product_stock = order_details[2]
        #warehouse_id = order_details[3]

        # Check if sufficient stock is available
        if product_stock >= ordered_quantity:
            # Update product stock in the Product table
            cursor.execute("""
            UPDATE Product SET quantity = quantity - %s
            WHERE product_id = %s""", (ordered_quantity, product_id))
            conn.commit()
            # Update order status to 'packed'
            cursor.execute("UPDATE Order SET status = 'packed' WHERE id = %s", (orderid,))
            conn.commit()
              
    else:
        print("Order not found.")

    # Cleanup
    cursor.close()
    conn.close()
    
    

    
    
    
    
