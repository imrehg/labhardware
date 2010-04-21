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
        self._NElement = 128
        self._MaxValue = 4096
        self._pixels = []
        for M in xrange(self._NMask):
            Mask = []
            for F in xrange(self._NFrame):
                Frame = [0]*self._NElement
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

    def blockquery(self):
        return self._pixels[self._Mask][self._Frame]

    def blockset(self, values):
        self._pixels[self._Mask][self._Frame] = values
        return

    def cmdmask(self, command):
        if command == '?':
            return self._Mask
        else:
            try:
                m = int(command)
            except:
                return
            if m in range(self._NMask):
                self._Mask = m
            return

    def cmdframe(self, command):
        if command == '?':
            return self._Frame
        else:
            try:
                f = int(command)
            except:
                return
            if f in range(self._NFrame):
                self._Frame = f
            return

    def cmdelement(self, command):
        if command == '?':
            return self._Element
        else:
            try:
                e = int(command)
            except:
                return
            if e in range(self._NElement):
                self._Element = e
            return

    def cmdvalue(self, command):
        if command == '?':
            return self._pixels[self._Mask][self._Frame][self._Element]
        else:
            try:
                v = int(command)
            except:
                return
            if 0 <= v < self._MaxValue:
                self._pixels[self._Mask][self._Frame][self._Element] = v
            return

    def maxmask(self):
        return self._NMask

    def maxframe(self):
        return self._NFrame

    def maxelement(self):
        return self._NElement

    def maxvalue(self):
        return self._MaxValue

    def clearframe(self):
        for e in xrange(self._NElement):
            self._pixels[self._Mask][self._Frame][e] = 0
                
    def activeframe(self, frame):
        pass
