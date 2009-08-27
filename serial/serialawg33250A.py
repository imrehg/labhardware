#!/usr/bin/env python

# RS-232 serial support for Agilent 33250A
# Be careful about the line endings. Handles SCPI commands and see manual
# http://cp.literature.agilent.com/litweb/pdf/33250-90002.pdf

import serial
from time import sleep
import random

# Values set on unit manually (but these are standard settings)
ser = serial.Serial('/dev/ttyUSB1',baudrate=57600, bytesize=8, stopbits=1, \
    parity=serial.PARITY_NONE, timeout=3, dsrdtr=1)

ser.open()
print ser

DEBUG = 0

def sendCmd(command):
    if DEBUG:
        print "%s" %(command.strip())
    # line ending is essential!
    ser.write("%s\n" %(command))

# Do a few random frequency changes
try:
    sendCmd("*rst")
    n = 0
    while n < 3:
        # random shapes
        randfunc = int(random.random()*3)
        func = {
            0 : lambda : 'sin',
            1 : lambda : 'square',
            2 : lambda : 'ramp',
        }[randfunc]()
        sendCmd("function %s" %(func))
        freq = int(random.random() * 100)
        print "Set frequency: %d kHz" %(freq)
        sendCmd("freq %d.0E+3" %(freq))
        #~ # needs delay before functuon shape can be queried
        sleep(1)
        sendCmd("freq?")
        line = ser.readline().strip()
        print "Frequency: %s" % (line)
        n += 1
        sleep(3)
except (KeyboardInterrupt):
    # Exit with Control-C
    pass
except:
    raise
finally:
    ser.close()
