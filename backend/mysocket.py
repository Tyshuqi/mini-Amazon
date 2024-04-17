from mysocket import *
from google.protobuf.internal.decoder import _DecodeVarint32
from google.protobuf.internal.encoder import _EncodeVarint

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
    server_fd.bind((host, port))
    # Queue up to 5 requests
    server_fd.listen(5)
    webapp_socket, addr = server_fd.accept()
    return webapp_socket
    
    
# def sendRequest(req_type, fd):
#     data = req_type.SerializeToString()
#     size = req_type.ByteSize()
#     fd.sendall(size + data)
    
def sendRequest(fd, req_type):
    req_type_string = req_type.SerializeToString()
    _EncodeVarint(fd.send, len(req_type_string), None)  # Encodes and sends the length
    fd.send(req_type_string)  # Then send the message
    
    
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






    