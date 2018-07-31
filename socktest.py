#!/usr/bin/python2

import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("spiegel.de",80))
request = "GET / HTTP/1.1\r\nHost: www.spiegel.de\r\n\r\n"
s.sendall(request)
while True:
    res = s.recv(1024)
    if not res:
        s.close()
        break
    print res
