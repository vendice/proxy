#!/usr/bin/python2

import socket
import httplib

#s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#s.connect(("www.example.com",80))
#request = "GET / HTTP/1.1\r\nHost: www.example.com\r\n\r\n"
#s.sendall(request)
#res = s.recv(4096)
#print res

#ssl_context = ssl.create_default_context()
conn = httplib.HTTPSConnection("192.168.2.128", port=53883)
conn.set_tunnel("www.spiegel.de",443)
conn.request("GET", "/")

r = conn.getresponse()
print r.read() 
print r.status

