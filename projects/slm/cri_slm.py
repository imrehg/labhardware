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

slm = SLM('/dev/ttyUSB0')

# set all levels to a previously known transmission level
drive = [820, 0]
for m in [0, 1]:
    slm.set("M %d" %(m))
    for i in xrange(0, 128):
        slm.set("E %d" %(i))
        slm.set("D %d" %(drive[m]))
    queries = ["M?", "E?", "D?"]
    for q in queries:
        print slm.query(q)
