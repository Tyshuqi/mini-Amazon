import socket
from google.protobuf.internal.decoder import _DecodeVarint32
from google.protobuf.internal.encoder import _EncodeVarint


# connect to world, ups
def clientSocket(host, port):
    # build
    print("BEGINNING clientSocket...")
    client_fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # connect
    client_fd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    client_fd.bind(('127.0.0.1', 8090))
    client_fd.connect((host, port))
    print("client fd is:", client_fd)
    return client_fd

# accept webapp client
def serverSocket(host, port):
    # Create a socket object
    server_fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Bind to the port
    server_fd.bind((host, port))
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
    # var_int_buff = []
    # while True:
    #     buf = fd.recv(1)
    #     var_int_buff += buf
    #     msg_len, new_pos = _DecodeVarint32(var_int_buff, 0)
    #     if new_pos != 0:
    #         break
    # whole_message = fd.recv(msg_len)  # string

    # response = res_type()
    # response.ParseFromString(whole_message)
    # return response
    var_int_buff = b''  # Use bytes instead of a list
    while True:
        print("Type of fd:", type(fd))
        buf = fd.recv(1)
        if not buf:
            raise ConnectionError("Connection closed by the remote server")
        var_int_buff += buf
        msg_len, new_pos = _DecodeVarint32(var_int_buff, 0)
        if new_pos != 0:
            break
    whole_message = fd.recv(msg_len)  # Read the whole message based on the length prefix
    if len(whole_message) < msg_len:
        raise IOError("Failed to receive the entire message")

    response = res_type()
    response.ParseFromString(whole_message)
    return response






    