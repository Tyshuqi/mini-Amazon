from google.protobuf.internal.decoder import _DecodeVarint32
from google.protobuf.internal.encoder import _EncodeVarint
import socket
import threading

# connect to world, ups
def clientSocket(host, port):
    # build
    client_fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # connect
    client_fd.connect((host, port))
    return client_fd

# accept webapp client
def serverSocket(host, port):
    # Create a socket object
    server_fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Bind to the port
    server_fd.bind(('0.0.0.0', port))
    # Queue up to 5 requests
    server_fd.listen(10)
    webapp_socket, addr = server_fd.accept()
    return webapp_socket
    

# convert message to string and send
def sendRequest(fd, req_msg):
    req_string = req_msg.SerializeToString()
    _EncodeVarint(fd.send, len(req_string), None)  # Encodes and sends the length
    fd.send(req_string)  # Then send the message
    
# receive string and convert to message  
def receiveResponse(fd, res_type):
    var_int_buff = []
    while True:
        buf = fd.recv(1)
        var_int_buff += buf
        msg_len, new_pos = _DecodeVarint32(var_int_buff, 0)
        if new_pos != 0:
            break
    whole_message = fd.recv(msg_len)  # string

    response = res_type()
    response.ParseFromString(whole_message)
    return response






    

def socket_connect(host, port):
    client_fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client_fd.connect((host, port))
        print(f"Connected to {host} on port {port}")
        return client_fd

        # client_socket.sendall(b"Hello, server!")
        
        # received_data = client_socket.recv(1024)
        # print(f"Received from server: {received_data.decode()}")
        
    except socket.error as e:
        print(f"Socket error: {e}")
    
    # finally:
    #     # Close the socket connection
    #     client_socket.close()
    #     print("Connection closed.")


class AckTracker:
    def __init__(self, start_seq=0):
        self.current_seq = start_seq
        self.pending_acks = set()
        self.lock = threading.Lock()

    def get_next_sequence_number(self):
        with self.lock:
            self.current_seq += 1
            return self.current_seq

    def add_request(self):
        seq_num = self.get_next_sequence_number()
        with self.lock:
            self.pending_acks.add(seq_num)   
        return seq_num

    def remove_ack(self, seq_num):
        with self.lock:
            if seq_num in self.pending_acks:
                self.pending_acks.discard(seq_num)
                

    def __str__(self):
        with self.lock:
            return str(self.pending_acks)

# Initialize AckTracker instance
ack_list = AckTracker()

# send request until receive ack
def checkAndSendReq(fd, req_msg, seqNum ):
    while True:
        # check ack in seq_list: resend
        if seqNum in ack_list.pending_acks:
            sendRequest(fd, req_msg)
            time.sleep(2)  # waits for 2 seconds
        # otherwise break
        else:
            break