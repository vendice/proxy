#!/usr/bin/python2

import socket
import threading
import time

HOST = ''
PORT = 53883
BLOCK_SIZE = 4096

connections = {}

def start_https_tunnel(client, host, port):
    """starts the tls tunnel betwenn client and serve
    it opens a new thread,and new socket to the server  so 2 threads are used one listens on the client and
    the other listens on the server for new data which is forwarded immediately
    args:
        client  - is a socket to the user agent
        host    - string name of the server
        port    - int prot of the server
    """
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
    """reads data on from_socket buffer and forwads the data to to_socket
    args:
        from_socket : the socket the data is read
        to_socket   : the socket the data is forwarded to
    """

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


def handle_connection(client, address):
    """ determines whether the request from the incoming connection is http or https and handles it approbiately
    if the request is has a CONNECT command a tls tunnel is initiated
    if the request is something different it will be forwarded to the host therefore it is checked whether a connection exists
    to the host when not a new (maybe two or more) one is created
    args:
        client  - the incoming connection
        address  - the address of the incomming connection
    """

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
        response = get_response(server)
        #response = server.recv(BLOCK_SIZE)
        print response
        client.sendall(response)

    client.close()


def parse_status_header(header):
    """parses header in a dictionary
    status             : status_line
    header_field_name  : value
    args:
        the header of the request or response
    return:
        dictionary 
    """

    header_dict = {}
    header_dict['status_line'] = header.split('\r\n')[0]
    header_fields = header.split('\r\n')[1:]
    for field in header_fields:
        if field != "": 
            key, value = field.split(': ')
            header_dict[key] = value
     return header_dict


def get_response(server):
    """reads the response from the server to the end and returns it
    Eceptions noch rein .... fuers empfangen 
    args:
        server  : socket to the server
    return:
        response string
    """
    while True:
        data = server.recv(BLOCK_SIZE)
        if "\r\n\r\n" in data:
            statusline_header, body = data.split("\r\n\r\n")
            header = parse_status_header(statusline_header)
            break
    while header[Content-Length] != len(body):
        body = body += server.recv(BLOCK_SIZE)
    return header + "\r\n\r\n" + body


def get_host_port (request):
    """determines the host and port to which the request should be sent
    fusionieren mit der header funktion moeglich???

    if a host field is given the host and port is retrieved from there,
    otherways it is retrieved from the URI
    args:
        request - request string
    return:
        host    - the host string
        port    - the port as integer
    """
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

    return host,  port


if __name__ == '__main__':
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind ((HOST, PORT))
    server.listen(1000)

    while True:
        client, address = server.accept()
        t = threading.Thread(target = handle_connection, args = (client, address))
        t.start() 






