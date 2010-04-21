#!/usr/bin/env python

# USB Serial support for CRI Spatial Light Modulator
#

import serial

class SLM:
    """
    Spatial Light Modulator
    """

    def __init__(self, serialport):
        """ Create motor controller serial interface
        Input:
        serialport : name of the serial port (eg. '/dev/ttyUSB0' or 'COM1')
        """
        self.iface = serial.Serial(serialport, baudrate=460800, bytesize=8, \
                                   stopbits=1, parity=serial.PARITY_NONE, \
                                   timeout=10, xonxoff=0, rtscts=0, dsrdtr=0)
        self.termchar = "\r"
        self._NMask = 2
        self._NFrame = 128
        self._NElement = 128
        self._MaxValue = 4096

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
            return int(self.query(target+command).split()[1])
        else:
            try:
                c = int(command)
                self.set("%s %d" %(target, c))
            except:
                pass
            finally:
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
