#!/usr/bin/env python

import serial
from time import sleep
import random

# Values set on unit manually (but these are standard settings)
ser = serial.Serial('/dev/ttyUSB0',baudrate=57600, bytesize=8, stopbits=1, \
    parity=serial.PARITY_NONE, timeout=3, dsrdtr=1)

ser.open()
print ser

DEBUG = 0

input = "/mnt/temp/tricky"

def sendCmd(command):
    if DEBUG:
        print "%s" %(command.strip())
    # line ending is essential!
    ser.write("%s\n" %(command))

try:
    while True:
        # random shapes
        randfunc = int(random.random()*3)
        freq = int(random.random() * 2000)

        inpara = open(input, "r")
        inpara.seek(0,0)
        inset = inpara.readline().strip()
        inpara.close()
        if (inset != ""):
            sp = inset.split(",")
            freq = float(sp[0])
            randfunc = int(sp[1])

        func = {
            0 : lambda : 'sin',
            1 : lambda : 'square',
            2 : lambda : 'ramp',
        }[randfunc]()
        sendCmd("function %s" %(func))

        print "Set frequency: %f Hz" %(freq)
        sendCmd("freq %d" %(freq))
        #~ # needs delay before functuon shape can be queried
        sleep(1)
        sendCmd("freq?")
        line = ser.readline().strip()
        print "Frequency: %s" % (line)
        sleep(3)

except (KeyboardInterrupt):
    # Exit with Control-C
    pass
except:
    raise
finally:
    ser.close()
