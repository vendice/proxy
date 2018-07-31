#!/usr/bin/python2

import socket
import threading
import time

HOST = ''
PORT = 53883
REQ_SIZE = 1024

def handle_connection(client, address):
    # takes care of the connection

    request = client.recv(REQ_SIZE)
    #print (request)
    request_host, request_port = get_host_port(request)
    out_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    out_socket.settimeout(15)
   # print request_host, request_port 
    out_socket.connect((request_host, request_port))
    out_socket.sendall(request)

    while True:
        response = out_socket.recv(1024)
        if (len(response) > 0):
            client.send(response)
        else:
            break

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
        address = lines[0].split('://')[1]
        host = address.split('/')[0]
    print host,port
    return host, port




server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind ((HOST, PORT))
server.listen(10)

while True:
    client, address = server.accept()
    t = threading.Thread(target = handle_connection, args = (client, address))
    t.start()






