#!/usr/bin/env python

# RS-232 serial support for Agilent 33120A 15MHz Arbitrary Waveform Generator
# Be careful about the line endings. Handles SCPI commands and see manual
# http://www.home.agilent.com/upload/cmc_upload/All/6C0633120A_USERSGUIDE_ENGLISH.pdf
# or look for it on the Internet Archive

import serial
from time import sleep
import random

# Values set on unit manually (but these are standard settings
ser = serial.Serial('/dev/ttyUSB1',baudrate=9600, bytesize=8, stopbits=1, \
    parity=serial.PARITY_NONE, timeout=3)

ser.open()
print ser

DEBUG = 0

def sendCmd(command):
    if DEBUG:
        print "%s" %(command).strip()
    # line ending is essential!
    ser.write("%s\n" %(command))

# Do a few random frequency changes
try:
    # enable remote mode
    sendCmd("system:remote")
    n = 0
    while n < 5:
        sendCmd("*cls")
        sendCmd("func:shape ramp")
        freq = int(random.random() * 100)
        print "Set frequency: %d kHz" %(freq)
        sendCmd("freq %d.0E+3" %(freq))
        # needs delay before functuon shape can be queried
        sleep(0.5)
        sendCmd("function:shape?")
        line = ser.readline().strip()
        print "Shape: %s" % (line)
        n += 1
        sleep(2)
except (KeyboardInterrupt):
    # Exit with Control-C
    pass
except:
    raise
finally:
    ser.close()
