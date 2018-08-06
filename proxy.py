#!/usr/bin/python2

import socket
import threading
import time

HOST = ''
PORT = 53883
BLOCK_SIZE = 4096


def transmit(from_socket,to_socket):
    # listens on from socket and transsmits data from one socket to another
    
    while True:
        data = from_socket.recv(BLOCK_SIZE)
        if not data:
            return
        to_socket.send(data)


def handle_connection(client, address):
    # takes care of the connection

    request = client.recv(BLOCK_SIZE)
    # print request
    request_host, request_port = get_host_port(request)
    out_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    out_socket.settimeout(30)
    out_socket.connect((request_host, request_port))

    if request[:7] == "CONNECT":
        client.sendall("HTTP/1.1 200 OK\r\n\r\n")
    else:
        out_socket.sendall(request)

    t = threading.Thread(target = transmit, args = (client, out_socket))
    t.start()

    transmit(out_socket, client)

    out_socket.close()
    client.close()

    return 0


def get_host_port (request):
    #returns the host and port, given the http request

    port = 80
    lines = request.split('\r\n')
    host = "errorurl"
    for line in lines:
        if line[:6] == "Host: ":
            host_addr = line.split(':')
            host = host_addr[1][1:]
            if len(host_addr) > 2:
                port = int(host_addr[-1])
            else:
                port = 80

    # kein host feld im body, erlaubt in http/1.0 
    
    if host == "errorurl":
        print lines[0]
        address = lines[0].split(' ')[1] #get address with path from GET or CONNECT...
    
         
                                                    #list index out of range ...?!?
        if address[:7] == 'http://':                #get ridof http or https
            port = 80
            host_path_port = address.split('://')[1]
        elif address[:8] == 'https://':
            port = 443
            host_path_port = address.split('://')[1]
        else:
            host_path_port = address

        host_path_array = host_path_port.split(':')
        if len(host_path_array) > 1:
            port = int(host_path_array[-1])
        host_path = host_path_array[0]
        host = host_path.split('/')[0]

    print host,port
    return host, port


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind ((HOST, PORT))
server.listen(10)

while True:
    client, address = server.accept()
    t = threading.Thread(target = handle_connection, args = (client, address))
    t.start()






