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
    Aconnect = world.AConnect()
    Aconnect.isAmazon = True
    
    for warehouse in all_warehouse:
        new_wh = Aconnect.initwh.add()
        new_wh.id = warehouse[0]
        new_wh.x = warehouse[1]
        new_wh.y = warehouse[2]
    # send Aconnect to world     
    sendRequest(fd, Aconnect)
        
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
    
    # Create a cursor object
    cursor = conn.cursor()
    # select warehouse info
    cursor.execute('SELECT product_id, description, count FROM Product, Order WHERE Product.id = Order.productID AND Order.id = orderID')
    # Fetch data
    all_product = cursor.fetchall()
    
    
    Apack = world.APack()
    Aproduct = APack.AProduct()
    
    for product in all_product:
        newproduct = Apack.AProduct.add()
        newproduct.id = product[0]
        newproduct.description = product[1]
        newproduct.count = product[2]
        
    cursor.execute('SELECT whnum FROM Order WHERE Order.id = orderID')
    warehouseNum = cursor.fetchall()
    APack.whnum = warehouseNum
    
    Apack.shipid = orderID
    
    # generate a seq_num
    seqNum = ack_list.add_request()
    Apack.seqnum = seqNum
    
    
    # send APack until receive ack    
    #sendRequest(fd, APack)
    checkAndSend(fd, APack, seqNum)
        
    
    cursor.close()
    conn.close()
    
    # 
    
