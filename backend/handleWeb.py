
import psycopg2
from mysocket import *
from ack import ack_list
from checkAck import *
from psycopg2 import OperationalError
from protocal import amazon_ups_pb2 as ups
from connectdb import get_db_connection


def checkName(orderID):
    print("enter checkName!")    
    conn = get_db_connection()
    if not conn:
        return None
    cursor = conn.cursor()
    print("after cursor!")

    try:
        with conn:
            with conn.cursor() as cursor:
                cursor.execute('SELECT "upsUsername" FROM users_order WHERE id = %s', (orderID,))
                ups_Username = cursor.fetchone()[0]
                print("ups_Username: ", ups_Username)
                return ups_Username if ups_Username else None

    except psycopg2.Error as e:
        print(f"An error occurred while check name: {e}")
        conn.rollback()
        
    
def getOrderStatus(order_id):
    conn = get_db_connection()
    if conn is None:
        return None
    
    with conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT status FROM users_order WHERE id = %s", (order_id,))
            result = cursor.fetchone()
            return result[0] if result else None
        

def updateUpsIDsForPendingOrders(ups_id, upsUsername):
    conn = get_db_connection()
    if not conn:
        print("Database connection failed.")
        return []
    cursor = conn.cursor()

    updated_order_ids = []  # List to collect updated order IDs

    try:
        # Fetching pending order IDs for the given username
        fetch_query = 'SELECT id FROM "users_order" WHERE "upsUsername" = %s AND status = %s'
        cursor.execute(fetch_query, (upsUsername, "pending"))
        order_ids = [row[0] for row in cursor.fetchall()]

        # Updating each order
        update_query = 'UPDATE "users_order" SET "upsUserID" = %s WHERE id = %s'
        for orderID in order_ids:
            cursor.execute(update_query, (ups_id, orderID))
            if cursor.rowcount > 0:
                conn.commit()
                updated_order_ids.append(orderID)  # Collect the successfully updated order ID
                print(f"UPS ID {ups_id} has been added to users_order {orderID}")
            else:
                print(f"No such order with ID {orderID} exists to update.")

    except psycopg2.Error as e:
        print(f"An error occurred: {e}")
        conn.rollback()
    
    finally:
        cursor.close()
        conn.close()
    
    return updated_order_ids  # Return the list of updated order IDs


def updateOrderStatus(upsUsername, newStatus):

    conn = get_db_connection()
    if not conn:
        print("Database connection failed.")
        return []
    cursor = conn.cursor()

    updated_order_ids = []  # List to collect updated order IDs

    try:
        # Fetching pending order IDs for the given username
        fetch_query = 'SELECT id FROM "users_order" WHERE "upsUsername" = %s AND status = %s'
        cursor.execute(fetch_query, (upsUsername, "pending"))
        order_ids = [row[0] for row in cursor.fetchall()]

        # Updating each order
        update_query = 'UPDATE "users_order" SET status = %s WHERE id = %s'
        for orderID in order_ids:
            cursor.execute(update_query, (newStatus, orderID))
            if cursor.rowcount > 0:
                conn.commit()
                updated_order_ids.append(orderID)  # Collect the successfully updated order ID
                print(f"users_order status updated to {newStatus} for users_order ID {orderID}.")
            else:
                print(f"No such order with ID {orderID} exists to update status.")

    except psycopg2.Error as e:
        print(f"An error occurred: {e}")
        conn.rollback()
    
    finally:
        cursor.close()
        conn.close()


    
   