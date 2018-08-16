#!/usr/bin/python2

import socket
import threading
import time

HOST = ''
PORT = 53883
BLOCK_SIZE = 4096

connections = {}

def start_https_tunnel(client, host, port):
    #starts the http tunnel
    #it opens a new thread, so 2 threads are needed one listens on the client and
    #the other listens on the server
    #client is a socket from the user agent,
    #host and port is the server

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    server.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 10)
    server.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 10)
    server.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 3)

    server.connect((host, port))
    
    t = threading.Thread(target = tunnel, args = (client, server))
    t.start()
    tunnel(server, client)
    t.join()
    server.close()

def tunnel(from_socket, to_socket):
    #listens on from_socket and tunnels data to to_socket 
    

    while True:
        try:
            data = from_socket.recv(BLOCK_SIZE)
            if not data:
                # from_socket.close() # gute idee? eventuell muss noch was empfangen werden
                break
            to_socket.sendall(data)
        except socket.error as msg:
            print msg
            from_socket.close()
            to_socket.close()
            break


def handle_http_request(request, host, port):
    #sends the request to the server over a existing connection or creates a new one
    #handles also the response
    pass



def handle_connection(client, address):
    #takes care of the connection


    request = client.recv(BLOCK_SIZE) #nutzen noch ueberpruefen
    if request == "":
        print "######################################"
        time.sleep(0.4)
        request = client.recv(BLOCK_SIZE)
        if request == "":
            client.close()
            return

    host, port = get_host_port(request)

    if request[:7] == "CONNECT":
        client.sendall("HTTP/1.1 200 OK\r\n\r\n")
        start_https_tunnel(client, host, port)
    else:
        #handle_http_request(client, request, host, port)
        if (host,port) in connections:
            server = connections[(host, port)][0] #choose better
        else:
            #maybe 2 or more connections from the beginning
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.connect((host, port))
            connections[(host, port)] = [server]
        server.sendall(request)
        print request
        #response = get_response(server)
        response = server.recv(BLOCK_SIZE)
        print response
        client.sendall(response)

    client.close()
    return 0


def parse_status_header(header):
    #parses header in a dictionary
    #return dictionary 
    #key                : value
    #status             : status_line
    #header_field_name  : value
    #i.e::Content-Length: 10

    header_dict = {}
    header_dict['status_line'] = header.split('\r\n')[0]
    header_fields = header.split('\r\n')[1:]
    for field in header_fields:
        if field != "": 
            key, value = field.split(': ')
            header_dict[key] = value
    return header_dict


def get_response(server):
    #reads the response from the server and returns it

    data = server.recv(BLOCK_SIZE)
    if "\r\n\r\n" in data:
        statusline_header, body = data.split("\r\n\r\n")
        header = parse_status_header(statusline_header)
    

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
    # keine Umwandlung erlaubt es muss der full qualified domain name bleiben
    # betrachtet nicht alle Faelle wie z.b. user:pass@Host

    if host == "errorurl":
        address = lines[0].split(' ')[1] #get address with path from GET or CONNECT...
        if address[:7] == 'http://':                #get ridof http or https
            port = 80
            user_host_path_port = address.split('://')[1]
        elif address[:8] == 'https://':
            port = 443
            user_host_path_port = address.split('://')[1]
        else:
            user_host_path_port = address
        
        host_path_array = user_host_path_port.split(':')
        if len(host_path_array) > 1:
            port_str = "" 
            for d in host_path_array[-1]:
                if (ord(d) >= 48 and ord(d) <= 57):
                    port_str += d
                else:
                    break
            port = int(port_str)
            
        host_path = host_path_array[0]
        host = host_path.split('/')[0]

    return host, port


if __name__ == '__main__':
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind ((HOST, PORT))
    server.listen(1000)

    while True:
        client, address = server.accept()
        t = threading.Thread(target = handle_connection, args = (client, address))
        t.start()






