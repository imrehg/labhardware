#!/usr/bin/env python

from socket import *
import sys
import serial
from re import match

BUFSIZ = 4096
HOST = ''
PORT = 30222
ADDR = (HOST,PORT)
counter = 0 

class ServCmd:
    def __init__(self, wavemeter):
        self.__serv = socket( AF_INET,SOCK_STREAM)
        self.__serv.bind((ADDR))
        self.__cli = None
        self.__imlistening  = 0
        self.__improcessing = 0
        self.wavemeter = wavemeter
        self.__run()
  
    def __run(self):
        self.__imlistening = 1
        while self.__imlistening:
            self.__listen()
            self.__improcessing = 1
            while self.__improcessing:
                self.__procCmd()
            self.__cli.close()
        self.__serv.close()
  
    def __listen(self):
        self.__serv.listen(5)
        print '...listening'
        cli,addr = self.__serv.accept()
        self.__cli = cli
        print '...connected: ', addr
  
    def __procCmd(self):
        cmd = self.__cli.recv(BUFSIZ)
        if not cmd: return
#        print cmd
        self.__servCmd(cmd)
        if self.__improcessing: 
            if cmd == 'WAVELENGTH':
                wavelength = self.wavemeter.QueryWavelength()
                print wavelength
                self.__cli.send("%s" %(wavelength))
            else:
                self.__cli.send('?')
  
    def __servCmd(self, cmd):
        cmd = cmd.strip()
        if cmd == 'BYE': 
            self.__improcessing = 0

class Wavemeter:
    def __init__(self, com):
        self.ser = serial.Serial(port="COM%d"%(com),baudrate=19200, bytesize=8, stopbits=1, \
            parity=serial.PARITY_NONE, timeout=1)
        print "Connected to: %s " %(self.ser.portstr)

    def close(self):
        print "Closing COM port"
        self.ser.close()
        
    def __SendCmd(self, cmd):
        cmdout = "@%c\r\n" %(cmd)
        self.ser.write(cmdout)
        
    def __GetReply(self):
        return self.ser.readline()
        
    def __ParseReply(self, reply):
        ''' Parse return string to get wavelength and other
        status parameters. '''
        return reply[0:11]
        
    def QueryWavelength(self):
        ''' Query wavelength by sending query command, reading
        response and parse reply '''
        self.__SendCmd(0x51)
        reply = self.__GetReply()        
        # Test reply:
        # reply = "+00631.9911,2A49,0200\r\n"
        wavelength = self.__ParseReply(reply)
        return wavelength

def saveip(location, ip):
    ''' Save IP address in shared area, so client script can connect '''
    ipdata = gethostbyaddr(gethostname())[2]
    for i in range(0,len(ipdata)):
        if  match('^192',ipdata[i]):
            ip = ipdata[i]
            print "IP: %s" %(ip)
            break
    if len(ip) == 0:
        return 1
    waveip = open(location,"w")
    waveip.write("%s:%d" %(ip,PORT))
    waveip.close()
    return 0

if __name__ == '__main__':
    ''' Check Command Line, at least 1 but maybe 2 arguments needed'''
    if (len(sys.argv) < 2):
        exit()

    ''' Get IP address '''
    if saveip("//Labserver/labdata/Software/waveip", ''):
        print "IP address cannot be found - checking command line"
        if (len(sys.argv) == 3):
            saveip("//Labserver/labdata/Software/waveip", sys.argv[2])
        else:
            exit()
        
    ''' Get desired COM port '''
    com = int(sys.argv[1])
    
    ''' Connect to wavemeter '''
    wavemeter = Wavemeter(com)
    serv = ServCmd(wavemeter)
    
    wavemeter.close()
    print "Finish"
