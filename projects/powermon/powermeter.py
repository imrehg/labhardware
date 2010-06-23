#!/usr/bin/env python

import serial
import os

class PowerMeter():
    """ Newport Optical Power Meter 1830-C """

    def __init__(self):
        if os.name == "posix":
            portbase = '/dev/ttyUSB'
        else:
            portbase == 'COM'

        for i in xrange(10):
            try:
                self.ser = serial.Serial("%s%d" %(portbase, i),
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
        else:
            print "Powermeter connected"

    def sendCom(self, command):
        self.ser.write("%s\n" % (command))

    def readReply(self):
        return(self.ser.readline().strip())

    def getReading(self):
        self.sendCom("D?")
        value = self.readReply();
        try:
            fvalue = float(value)
        except:
            fvalue = None
        return(fvalue)

if __name__ == "__main__":
    powermeter = PowerMeter()
