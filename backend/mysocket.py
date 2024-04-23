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
    #client_fd.bind(('127.0.0.1', 8090))
    client_fd.connect((host, port))
    print("client fd is:", client_fd)
    return client_fd

# listen webapp client
def serverSocket(host, port):
    # Create a socket object
    server_fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Bind to the port
    server_fd.bind(('0.0.0.0', port))
    # Queue up to 5 requests
    server_fd.listen(10)
    # webapp_socket, addr = server_fd.accept()
    return server_fd
    

# convert message to string and send
def sendRequest(fd, req_msg):
    req_string = req_msg.SerializeToString()
    _EncodeVarint(fd.send, len(req_string), None)  # Encodes and sends the length
    fd.send(req_string)  # Then send the message
    
#receive string and convert to message  
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






def CreceiveResponse(sock, response_type):
    data = read_varint_delimited_stream(sock)
    response = response_type()
    response.ParseFromString(data)
    return response
    

# read google buffer protocol response from a socket, return the raw data
def read_varint_delimited_stream(sock):
    size_variant = b''
    while True:
        size_variant += sock.recv(1)
        try:
            size = _DecodeVarint32(size_variant, 0)[0]
        except IndexError:
            continue # if decode failed, read one more byte from stream
        break # else if decode succeeded, break. Size is available
    data = sock.recv(size) # data in string format
    return data