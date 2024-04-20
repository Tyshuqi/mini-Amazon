import psycopg2
from mysocket import *
from server import ack_list
from checkAck import *
from psycopg2 import OperationalError
import amazon_ups_pb2 as ups
from connectdb import get_db_connection



def toOrderTruck(fd, orderID):
    conn = get_db_connection()
    if not conn:
        return 
    cursor = conn.cursor()

    try:
        ordertruck_msg = ups.AOrderTruck()
        # Fetch OrderItem, Product, Warehouse, and Order details for the given orderID
        cursor.execute("""
            SELECT p.id, p.description, oi.quantity, w.id, w.x, w.y, oi.upsUsername, o.des_x, o.des_y
            FROM OrderItem oi
            JOIN Product p ON oi.product_id = p.id
            JOIN Warehouse w ON p.warehouse_id = w.id
            JOIN Order o ON oi.order_id = o.id
            WHERE oi.order_id = %s
        """, (orderID,))

        for row in cursor.fetchall():
            product_info = ups.product(
                productID=row[0],
                description=row[1],
                count=row[2]
            )
            warehouse_info = ups.warehouse(
                warehouseID=row[3],
                x=row[4],
                y=row[5]
            )
            destination_info = ups.destination(
                x=row[7],
                y=row[8]
            )

            # Populate the AOrderTruck message
            ordertruck_msg.packageID = orderID
            ordertruck_msg.productInfo.CopyFrom(product_info)
            ordertruck_msg.warehouseInfo.CopyFrom(warehouse_info)
            ordertruck_msg.destinationInfo.CopyFrom(destination_info)
            ordertruck_msg.upsUsername = row[6]
            # generate a seq_num
            seqNum = ack_list.add_request()
            ordertruck_msg.seqnum = seqNum
            checkAndSendReq(fd, ordertruck_msg, seqNum)
    
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()
    
    
    
def startDelivery(fd, orderID):
    conn = get_db_connection()
    if not conn:
        return 
    cursor = conn.cursor()
    
    try:
        # Update the order status to 'delivering' before sending the delivery command
        update_query = "UPDATE Order SET status = %s WHERE id = %s"
        cursor.execute(update_query, ('delivering', orderID))
        conn.commit()

        # Preparing the message for delivery start
        req_msg = ups.ACommand()
        startDelivery_msg = req_msg.toStart.add()
        startDelivery_msg.packageID = orderID
        
        # Generate a seq_num
        seqNum = ack_list.add_request()
        startDelivery_msg.seqnum = seqNum

        # Send until receive acks
        checkAndSendReq(fd, req_msg, seqNum)

        print("Delivery started for order ID:", orderID)

    except psycopg2.Error as e:
        print(f"An error occurred while updating order status or sending start delivery message: {e}")
        conn.rollback()

    finally:
        cursor.close()
        conn.close()


def delivered(fd, orderID):
    conn = get_db_connection()
    if not conn:
        return 
    cursor = conn.cursor()
    
    try:
        # Update the order status to 'delivered'
        update_query = "UPDATE Order SET status = %s WHERE id = %s"
        cursor.execute(update_query, ('delivered', orderID))
        conn.commit()
        print(f"Order {orderID} has been marked as delivered.")

    except psycopg2.Error as e:
        # If an error occurs, print an error message and rollback any changes
        print(f"An error occurred while updating the order status to 'delivered': {e}")
        conn.rollback()

    finally:
        # Clean up by closing cursor and connection
        cursor.close()
        conn.close()