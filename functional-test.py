#!/usr/bin/python2

from selenium import webdriver
import time
import unittest

'''Steht die url auf einer Blacklist dann wird der request nicht weitergeleitet, stattdessen wird ein
html Dokument gesendet, dass den Nutzer darauf hinweit dass die Seite gesoerrt ist.
Die Blacklist beinhaltet auch noch Uhrzeiten, d.h. wenn der Nutzer diesselbe Seite nach 20.00 Uhr
aufrufen will so geling dies.'''


class ProxyTest (unittest.TestCase):

    def setUp (self):
        proxy = "192.168.2.128"
        port = 53883

        fp = webdriver.FirefoxProfile()

        fp.set_preference("network.proxy.type", 1)
        fp.set_preference("network.proxy.http", proxy)
        fp.set_preference("network.proxy.http_port", port)
       # fp.set_preference("network.proxy.https", proxy)
       # fp.set_preference("network.proxy.https_port", port)
        fp.set_preference("network.proxy.ssl", proxy)
        fp.set_preference("network.proxy.ssl_port", port)
        fp.set_preference("general.useragent.override","Mozilla/5.0")

        fp.update_preferences()

        self.browser = webdriver.Firefox(firefox_profile=fp)

    def tearDown(self):
        self.browser.quit()


    def test_https_passthrough(self):

        '''Mann kann eine Verbindung zum Proxy aufbauen und im Normalfall leitet er http und https         Verbindungen einfach weiter.'''
        
        self.browser.get('https://static.vee24.com')
        self.assertIn('static.vee24.com test page', self.browser.title)
        text = self.browser.find_element_by_tag_name('p').text
        self.assertIn('OK', text)


    def test_http_passthrough(self):
        # tests http connection with different address formats
        
        self.browser.get('http://www.example.com')
        self.assertIn('Example Domain', self.browser.title)

       # self.browser.get('http://www.spiegel.de')
       # self.assertIn('SPIEGEL ONLINE', self.browser.title)

if __name__ == '__main__':
    unittest.main()
