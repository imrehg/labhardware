#!/usr/bin/env python
# a simple TCP client
  
from socket import * 
from time import time
from time import sleep 
import sys 
import string
BUFSIZE = 4096
  
class CmdLine:
    def __init__(s,host,port):
        s.__HOST = host
        s.__PORT = port
        s.__ADDR = (s.__HOST,s.__PORT)
        s.__sock = None
  
    def makeConnection(s):
        s.__sock = socket( AF_INET,SOCK_STREAM)
        s.__sock.settimeout(3.0)
        s.__sock.connect(s.__ADDR)
  
    def sendCmd(s, cmd):
        s.__sock.send(cmd)
  
    def getResults(s):
        data = s.__sock.recv(BUFSIZE)
        return data
   
if __name__ == '__main__':
    remote = open('/srv/labdata/Software/waveip',"r")
    addr = remote.readline()
    info = string.split(addr,':')
    host = info[0]
    port = int(info[1])

    goodconnection = True
    try:
        conn = CmdLine(host,port)
        conn.makeConnection()
        conn.sendCmd('WAVELENGTH')
        message = conn.getResults()
        conn.sendCmd('BYE') 
    except:
        goodconnection = False
        message = "<i>Cannot connect to Wavenet server, \
                   please check if server functions properly \
                   and refresh this page</i>"

    print "Content-type: text\html\n\n"
    print "<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Strict//EN\" \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd\">"
    print "<html><head>"
    if (goodconnection):
       print "<meta http-equiv=\"refresh\" content=\"1\" >"
    print "<title>WA-1500 wavemeter</title> \
         </head><body>"
    print "<h1>%s</h1>" %(message)
    print "</body></html>"
