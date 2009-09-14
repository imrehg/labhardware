#!/usr/bin/env python

import SocketServer
import sys
import serial
from re import match

BUFSIZ = 4096
DEFAULTPORT = 31234

class WaveUDPServer(SocketServer.UDPServer):
    ''' Our UDP server to reply to client requests for wavemeter
    information.'''

    def __init__(self, address, HandlerClass, wavemeter):
        ''' Overwrite __init__ so we can pass the wavemeter object to the
        request handler.'''
        self.wavemeter = wavemeter
        SocketServer.UDPServer.__init__(self, address, HandlerClass)

    def finish_request(self, request, client):
        ''' Reply to request of remote clients '''
        self.RequestHandlerClass(request, client, self, self.wavemeter)

class WaveUDPRequestHandler(SocketServer.BaseRequestHandler):

    def __init__(self, request, client, server, wavemeter):
        self.wavemeter = wavemeter
        SocketServer.BaseRequestHandler.__init__(self, request, client, server)

    def handle(self):
        cmd = self.request[0].strip()
        socket = self.request[1]
        reply = self.__procCmd(cmd)
        socket.sendto(reply, self.client_address)

    def __procCmd(self, cmd):
        print "From %s got query: %s" %(self.client_address[0], cmd)
        if cmd == 'WAVELENGTH':
            wavelength = self.wavemeter.QueryWavelength()
            reply = " %s " %(wavelength)
        else:
            reply = "?"
        return reply

class Wavemeter:
    def __init__(self, com, baud):
        self.ser = serial.Serial(port="%s"%(com),baudrate=baud, bytesize=8, stopbits=1, \
            parity=serial.PARITY_NONE, timeout=1)
        print "Connected to: %s " %(self.ser.portstr)
        if (not self.__TestConnection()):
            print "No Wavemeter on this port...."
            self.close()
            return None

    def close(self):
        print "Closing COM port"
        self.ser.close()
        
    def __TestConnection(self):
        self.__SendCmd(0x51)
        reply = self.__GetReply().strip()
        if (match("^.{11},[0-9A-F]{4},[0-9A-F]{4}", reply)):
            found = True
        else:
            found = False
        return found

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

def getip(port, fix_ip=None, ip_mask=None, saveto=None):
    # ''' Save IP address in shared area, so client script can connect '''
    ip = None
    if fix_ip:
        ip = fix_ip
    elif ip_mask:
        import netifaces
        for interface in netifaces.interfaces():
            for data in netifaces.ifaddresses(interface)[netifaces.AF_INET]:
                tempip = data['addr']
                if (match(ip_mask, tempip)):
                    ip = tempip
                break
            if (ip):
                break
    if ip:
        print "IP set: %s" %(ip)
        if (saveto):
            waveip = open(saveto,"w")
            waveip.write("%s:%d" %(ip,port))
            waveip.close()
            print "IP:PORT saved to %s" %(saveto)
    else:
        print "cannot set IP address..."
    
def getconfig(config, section, setting, getint=False):
    try:
        if (getint):
            value = config.getint(section, setting)
        else:
            value = config.get(section, setting)
    except:
        value = None
    return value

if __name__ == '__main__':
    import ConfigParser

    config = ConfigParser.ConfigParser()
    configfile = 'wavenetserver.cfg'
    if (len(sys.argv) == 2):
        configfile = sys.argv[1]
    try:
        config.read(configfile)
    except:
        print("Cannot open configuration file: %s" %(configfile))
        raw_input("Press any key to exit ...")
        exit()

    # Connect to Wavemeter over COM port
    combase = config.get('COM', 'combase')
    baud = config.getint('COM', 'baud')
    wavemeter = None
    for i in range(0, 10):
        try:
            wavemeter = Wavemeter("%s%d" %(combase, i), baud)
        except:
            continue
        if (not wavemeter):
            continue
        else:
            break
    if (not wavemeter):
        print "No wavemeter found with current settings."
        raw_input("Press any key to exit ...")
        exit()

    # Get IP
    fix_ip = getconfig(config, 'IP', 'fix_ip')
    ip_mask = getconfig(config, 'IP', 'ip_mask')
    ip_file = getconfig(config, 'IP', 'ip_file')
    port = getconfig(config, 'IP', 'port', getint=True)
    if port == None :
        port = DEFAULTPORT
    getip(port=port, fix_ip=fix_ip, ip_mask=ip_mask, saveto=ip_file)

    # Start server
    server = WaveUDPServer(('', port), WaveUDPRequestHandler, wavemeter)
    try:
        server.serve_forever()
    except ( KeyboardInterrupt , SystemExit ) :
        pass
    except:
        raise
    finally:
        wavemeter.close()
        print "Finished"
