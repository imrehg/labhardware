#!/usr/bin/env python

# USB Serial support for CRI Spatial Light Modulator
#

import serial
import os

class SLM:
    """
    Spatial Light Modulator
    """

    def __init__(self, serialport=None):
        """ Create motor controller serial interface
        Input:
        serialport : name of the serial port (eg. '/dev/ttyUSB0' or 'COM1')
        """
        self.termchar = "\r"
        if (serialport is None):
            if (os.name == 'nt'):
                serialbase = "COM"
                serialnumstart = 1
            else:
                serialbase = "/dev/ttyUSB"
                serialnumstart = 0
            for i in xrange(serialnumstart, 20):
                serialport = "%s%d" %(serialbase,i)
                self.iface = self.__connectport(serialport)
                if not (self.iface is None) and self.getversion():
                    break
        else:
            self.iface = self.__connectport(serialport)

        if self.iface is None:
            print("Not connected...")
        else:
            print("Translation stage connected on %s" %(serialport))

        self._NMask = 2
        self._NFrame = 128
        self._NElement = 128
        self._MaxValue = 4096

    def __connectport(self, serialport):
        try:
            iface = serial.Serial(serialport, baudrate=460800, bytesize=8, \
                                      stopbits=1, parity=serial.PARITY_NONE, \
                                      timeout=10, xonxoff=0, rtscts=0, dsrdtr=0)
        except:
            iface = None
        return iface

    def set(self, command):
        """ Send command to controller, and read answer if there's any
        For correct behaviour, it seems we have to read at least one line
        """
        self.iface.write(command+self.termchar)
        self.iface.readline(eol=self.termchar)

    def query(self, command):
        self.set(command)
        resp = self.iface.readline(eol=self.termchar).strip()
        return resp

    def _cmdproto(self, target, command):
        if  command == '?':
            try:
                answer = int(self.query(target+command).split()[1])
            except:
                answer = None
            return answer
        else:
            try:
                c = int(command)
                self.set("%s %d" %(target, c))
            except:
                pass
            finally:
                return

    def blockquery(self):
        self.set("B?")
        r = self.iface.read(self._NElement*2)
        values = []
        for i in xrange(0,self._NElement*2,2):
            values.append(ord(r[i+1])*256 + ord(r[i]))
        return values

    def blockset(self, values):
        if len(values) <> self._NElement:
            return
        out = ""
        for i in range(self._NElement):
            out += chr(values[i]%256)+chr(values[i]/256)
        self.set("B1")
        self.iface.write(out)
        return

    def cmdmask(self, command):
        return self._cmdproto('M', command)

    def cmdframe(self, command):
        return self._cmdproto('F', command)

    def cmdelement(self, command):
        return self._cmdproto('E', command)

    def cmdvalue(self, command):
        return self._cmdproto('D', command)

    def maxmask(self):
        return self._NMask

    def maxframe(self):
        return self._NFrame

    def maxelement(self):
        return self._NElement

    def maxvalue(self):
        return self._MaxValue

    def clearframe(self):
        self.set("C 1")
                
    def activeframe(self, frame):
        self.set("P %d" %frame)

    def getversion(self):
        return self._cmdproto('V', '?')
