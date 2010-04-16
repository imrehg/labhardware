#!/usr/bin/env python

# USB Serial support for CRI Spatial Light Modulator
#

import serial
import re

class SLM:
    """
    Spatial Light Modulator
    """

    def __init__(self, serialport):
        """ Create motor controller serial interface
        Input:
        serialport : name of the serial port (eg. '/dev/ttyUSB0' or 'COM1')
        """
        self._Mask = 0
        self._NMask = 2
        self._Frame = 0
        self._NFrame = 128
        self._Element = 0
        self._NElements = 128
        self._pixels = []
        for M in xrange(self._NMask):
            Mask = []
            for F in xrange(self._NFrame):
                Frame = [0]*self._NElements
                Mask.append(Frame)
            self._pixels.append(Mask)

    def set(self, command):
        """ Send command to controller, and read answer if there's any
        For correct behaviour, it seems we have to read at least one line
        """
        # Set mask
        mask = re.compile("^M\s*([?|\d+])$")
        frame = re.compile("^F\s*([?|\d+])$")
        element = re.compile("^E\s*([?]|\d+)$")
        if mask.search(command):
            c = mask.match(command).group(1)
            if not (c == '?'):
                self._Mask = int(c)
        elif frame.search(command):
            c = frame.match(command).group(1)
            if  not (c == '?'):
                self._Frame = int(c)
        elif element.search(command):
            c = element.match(command).group(1)
            if not (c == '?'):
                self._Element = int(c)
        else:
            print "Wot?"
        print self._Mask, self._Frame, self._Element
    def query(self, command):
        self.set(command)
        resp = self.iface.readline(eol=self.termchar).strip()
        return resp

slm = SLM('/dev/ttyUSB0')
slm.set("E 10")
slm.set("F 1")
slm.set("E ?")
# # set all levels to a previously known transmission level
# drive = [820, 0]
# for m in [0, 1]:
#     slm.set("M %d" %(m))
#     for i in xrange(0, 128):
#         slm.set("E %d" %(i))
#         slm.set("D %d" %(drive[m]))
#     queries = ["M?", "E?", "D?"]
#     for q in queries:
#         print slm.query(q)
