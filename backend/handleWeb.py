from connectdb import get_db_connection


def checkName(orderID):
    conn = get_db_connection()
    if not conn:
        return None
    cursor = conn.cursor()
    
    with conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT upsUsername FROM users_order WHERE id = %s", (orderID))
            ups_Username = cursor.fetchone()[0]
            return ups_Username if ups_Username else None
        
    
def getOrderStatus(order_id):
    conn = get_db_connection()
    if conn is None:
        return None
    
    with conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT status FROM users_order WHERE id = %s", (order_id,))
            result = cursor.fetchone()
            return result[0] if result else None
        
        
def updateUpsID(ups_id, orderID):
    conn = get_db_connection()
    if not conn:
        print("Database connection failed.")
        return 
    cursor = conn.cursor()
    
    try:
        update_query = 'UPDATE "users_order" SET upsUserID = %s WHERE id = %s'
        cursor.execute(update_query, (ups_id, orderID))
        if cursor.rowcount == 0:
            print(f"No such order with ID {orderID} exists to update.")
        else:
            conn.commit()
            print(f"UPS ID {ups_id} has been added to users_order {orderID}")
    
    except psycopg2.Error as e:
        print(f"An error occurred while updating the UPS ID for users_order ID {orderID}: {e}")
        conn.rollback()
    
    finally:
        cursor.close()
        conn.close()

    
def updateOrderStatus(orderID, newStatus):
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to the database.")
        return
    
    cursor = conn.cursor()
    
    try:
        # Update the status of the order
        update_query = 'UPDATE "users_order" SET status = %s WHERE id = %s'
        cursor.execute(update_query, (newStatus, orderID))
        
        if cursor.rowcount == 0:
            print(f"No order found with ID {orderID}.")
        else:
            conn.commit()
            print(f"users_order status updated to {newStatus} for users_order ID {orderID}.")
    
    except Exception as e:  # It's good to catch specific exceptions, adjust as needed
        print(f"An error occurred while updating the order status: {e}")
        conn.rollback()
    
    finally:
        cursor.close()
        conn.close()
