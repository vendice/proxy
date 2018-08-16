#!/usr/bin/python2

import proxy
import unittest

class ProxyTest(unittest.TestCase):

    def test_host_port_retrieve(self):
        #test the retrieval of host and port from the request
        #request could be a tunnel request or an http request with 
        #host field in the header or with an full qualified domain name

        request = "GET / HTTP/1.1\r\nHost: www.spiegel.de\r\n\r\n" 
        host, port = proxy.get_host_port(request) 
        self.assertEqual(host, "www.spiegel.de")
        self.assertEqual(port, 80)

        request = "GET http://www.spiegel.de:443/path/index.html HTTP/1.1" 
        host, port = proxy.get_host_port(request) 
        self.assertEqual(host, "www.spiegel.de")
        self.assertEqual(port, 443)

        request = "POST https://spiegel.de/path/index.html HTTP/1.1" 
        host, port = proxy.get_host_port(request) 
        self.assertEqual(host, "spiegel.de")
        self.assertEqual(port, 443)

        request = "CONNECT /path/index.html HTTP/1.1\r\nHost: spiegel.de:8080\r\n\r\n" 
        host, port = proxy.get_host_port(request) 
        self.assertEqual(host, "spiegel.de")
        self.assertEqual(port, 8080)

    def test_parse_message(self):
        response = '''HTTP/1.1 200 OK\r\nContent-Length: 10\r\n\r\nabcdefghij'''
        header = proxy.parse_status_header(response.split('\r\n\r\n')[0])
        self.assertEqual(header['status_line'], "HTTP/1.1 200 OK")
        self.assertEqual(header['Content-Length'], '10')

if __name__ == '__main__':
    unittest.main()
