import psycopg2
import world_amazon_pb2 as world
from mysocket import *
from server import ack_list
from checkAck import *
from psycopg2 import OperationalError
from connectdb import get_db_connection


def connect(fd):
    conn = get_db_connection()
    if not conn:
        return  
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
    conn = get_db_connection()
    if not conn:
        return 
    cursor = conn.cursor()
    
    try:
        # Select product info through the OrderItem model
        cursor.execute('''
        SELECT p.id, p.description, oi.quantity, w.id as warehouse_id
        FROM OrderItem oi
        JOIN Product p ON oi.product_id = p.id
        JOIN Warehouse w ON p.warehouse_id = w.id
        WHERE oi.order_id = %s;
        ''', (orderID,))
        all_product = cursor.fetchall()

        # Initialize the message structure for packaging
        req_msg = world.ACommands()
        pack_msg = req_msg.topack.add()
        for product in all_product:
            newproduct = pack_msg.things.add()
            newproduct.id = product[0]
            newproduct.description = product[1]
            newproduct.count = product[2]

        # Get warehouse number from the first product if available
        if all_product:
            pack_msg.whnum = all_product[0][3]
        else:
            print("No products found for this order.")
            return

        pack_msg.shipid = orderID  # Set shipid to orderID
        seqNum = ack_list.add_request()  # Generate a sequence number
        pack_msg.seqnum = seqNum

        # Send APack until receive ack
        checkAndSendReq(fd, req_msg, seqNum)

        # Update order status to 'packing'
        update_query = "UPDATE Order SET status = %s WHERE id = %s"
        cursor.execute(update_query, ('packing', orderID))
        conn.commit()

    except Exception as e:
        print(f"Error in toPack function: {e}")
        conn.rollback()

    finally:
        # Clean up
        cursor.close()
        conn.close()
        
        
    
def packed(fd, orderid):
    conn = get_db_connection()
    if not conn:
        return 
    cursor = conn.cursor()

    try:
        # Get all order items and their corresponding product stock information
        cursor.execute("""
        SELECT oi.product_id, oi.quantity as ordered_quantity, p.quantity as product_stock
        FROM OrderItem oi
        JOIN Product p ON oi.product_id = p.id
        WHERE oi.order_id = %s;
        """, (orderid,))
        order_items = cursor.fetchall()

        # Check if there is sufficient stock for all items and update accordingly
        all_items_can_be_packed = True
        for item in order_items:
            product_id, ordered_quantity, product_stock = item
            if product_stock < ordered_quantity:
                all_items_can_be_packed = False
                print(f"Insufficient stock for product ID {product_id}. Required: {ordered_quantity}, Available: {product_stock}")
                break
        
        if all_items_can_be_packed:
            # If all items can be packed, update the stock and order status
            for item in order_items:
                product_id, ordered_quantity, _ = item
                cursor.execute("""
                UPDATE Product SET quantity = quantity - %s
                WHERE id = %s;
                """, (ordered_quantity, product_id))
            
            cursor.execute("""
            UPDATE Order SET status = 'packed'
            WHERE id = %s;
            """, (orderid,))
            conn.commit()
            print("Order packed and product quantities updated.")
        else:
            # If not all items can be packed, do not commit any changes
            conn.rollback()
            print("Order not packed due to insufficient stock.")

    except psycopg2.Error as e:
        print(f"An error occurred: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


def toPurchaseMore(fd, productid, amount):
    conn = get_db_connection()
    if not conn:
        return 
    cursor = conn.cursor()

    try:
        # Select product description using a parameterized query to avoid SQL injection
        cursor.execute('SELECT description FROM Product WHERE id = %s', (productid,))
        product_description = cursor.fetchone()
        if not product_description:
            print("Product not found.")
            return
        product_description = product_description[0]
        
        req_msg = world.ACommands()
        purMore_msg = req_msg.buy.add()

        # Add product details to the message
        newproduct = purMore_msg.things.add()
        newproduct.id = productid
        newproduct.description = product_description
        newproduct.count = amount

        # Get warehouse ID using a parameterized query
        cursor.execute("""
            SELECT warehouse_id
            FROM Product
            WHERE id = %s;
        """, (productid,))
        warehouseNum = cursor.fetchone()
        if not warehouseNum:
            print("Warehouse not found for this product.")
            return
        warehouseNum = warehouseNum[0]

        purMore_msg.whnum = warehouseNum

        # Generate a sequence number
        seqNum = ack_list.add_request()
        purMore_msg.seqnum = seqNum

        # Send the message until an acknowledgment is received
        checkAndSendReq(fd, req_msg, seqNum)

    finally:
        # Cleanup: close cursor and connection
        cursor.close()
        conn.close()
    
    
    
def purchase_more_arrived(product_id, amount):
    conn = get_db_connection()
    if not conn:
        return 
    cursor = conn.cursor()
    
    try:    
        # Update the product stock in the Product table
        cursor.execute("""
            UPDATE Product 
            SET quantity = quantity + %s 
            WHERE id = %s;
        """, (amount, product_id))
        
        conn.commit()  # Commit the transaction
        print(f"Updated product {product_id}: quantity increased by {amount}.")

    except OperationalError as e:
        print(f"An error occurred: {e}")
    finally:
        # Cleanup: close cursor and connection
        if conn:
            cursor.close()
            conn.close()

    
def toLoad(fd, orderID, truckID):
    conn = get_db_connection()
    if not conn:
        return 
    cursor = conn.cursor()
    
    req_msg = world.ACommands()
    toLoad_msg = req_msg.load.add()
    try:
        # Get the warehouse ID for the products associated with the order
        cursor.execute("""
            SELECT DISTINCT warehouse.id
            FROM Warehouse
            JOIN Product ON Warehouse.id = Product.warehouse_id
            JOIN OrderItem ON Product.id = OrderItem.product_id
            WHERE OrderItem.order_id = %s
        """, (orderID,))
        
        # Fetch one warehouse ID (assuming all items in the order are from the same warehouse)
        warehouse_id = cursor.fetchone()[0]
        if warehouse_id is not None:
            print("Warehouse ID:", warehouse_id)
            # toLoad_msg = world.APutOnTruck()
            toLoad_msg.whnum = warehouse_id
            toLoad_msg.truckid = truckID
            toLoad_msg.shipid = orderID
            # generate a seq_num
            seqNum = ack_list.add_request()
            toLoad_msg.seqnum = seqNum
            # Send until receive acks
            checkAndSendReq(fd, req_msg, seqNum)
            
            # Update order status to 'loading'
            update_query = "UPDATE Order SET status = %s WHERE id = %s"
            cursor.execute(update_query, ('loading', orderID))
            conn.commit()
        else:
            print("No warehouse found for this order.")

    except Exception as e:
        print(f"Error during database operation: {e}")
    finally:
        cursor.close()
        conn.close()
    
    

def loaded(fd, orderID):
    conn = get_db_connection()
    if not conn:
        return 
    cursor = conn.cursor()

    try:
        # Update order status to 'loaded'
        cursor.execute("""
        UPDATE Order
        SET status = %s
        WHERE id = %s;
        """, ('loaded', orderID))

        # Commit the changes to the database
        conn.commit()
        print("Order status updated to 'loaded'.")
        
    except psycopg2.Error as e:
        # Print an error message and rollback in case of exception
        print(f"An error occurred while updating the order status: {e}")
        conn.rollback()
    
    finally:
        # Close the cursor and the connection
        cursor.close()
        conn.close()
        
        
