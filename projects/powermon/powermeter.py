#!/usr/bin/env python

import serial
import sys

class PowerMeter():

    def __init__(self):
        portbase = 'COM'
        for i in xrange(10):
            try:
                self.ser = serial.Serial("%s%d" %(porbase, i),
                                         baudrate=9600,
                                         bytesize=8,
                                         stopbits=1,
                                         parity=serial.PARITY_NONE,
                                         timeout=1,
                                         xonxoff=1)
                self.getReading()
                break
            except:
                self.ser = None
                pass
        if self.ser is None:
            print "No connection..."
            return None


    def sendCom(self, command):
        self.ser.write("%s\n" % (command))

    def readReply(self):
        return(self.ser.readline().strip())

    def getReading(self):
        self.sendCom("D?")
        value = float(self.readReply());
        return(value)

if __name__ == "__main__":
    print "Now?"
    powermeter = PowerMeter()
    print "Yeah!"
