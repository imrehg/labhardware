#!/usr/bin/env python

# RS-232 Serial support  for 3PK-345 Multimeter
# Find documentation separately
#
# TODO:
# Impement other reading types besides Voltage, Current and Resistance
# Interpret values
# Graphical interface
# Logging

import serial
import re
from time import time
import logging
logger = logging.getLogger('serialmulti')
hdlr = logging.FileHandler('./pump.log')
formatter = logging.Formatter('%(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)

def interpret(line):
    mode = line[0:2]
    value = line[2:9].strip()
    unit = line[9:-1].strip()

    now = time()

    if  (re.match('O.L',value)):
        value = 'inf'
 
    if (mode == 'OH'):
        print "Resistance: %s %s" % (value, unit)
    elif (mode == 'DC'):
        if (re.search('V',unit)):
            print "DC Voltage: %s %s" % (value, unit)
            logger.info("%f %s" % (now, value))
        if (re.search('A',unit)):
            print "DC Current: %s %s" % (value, unit)
    elif (mode == 'AC'):
        if (re.search('V',unit)):
            print "AC Voltage: %s %s" % (value, unit)
        if (re.search('A',unit)):
            print "AC Current: %s %s" % (value, unit)


# Setting up connection. Needs the many DTR/RTS things for some reason....
ser = serial.Serial('/dev/ttyUSB0',baudrate=600, bytesize=7, stopbits=2, \
    parity=serial.PARITY_NONE, timeout=1, xonxoff=1, rtscts=0, dsrdtr=1)
ser.setDTR(1)
ser.setRTS(0)
ser.setDTR(1)
ser.setRTS(0)
ser.setDTR(1)
ser.setRTS(0)
ser.setDTR(1)
ser.setRTS(0)
try:
    while True:
        ser.write("D")
        line = ser.readline()
        if ( re.match('^[ODA]+', line) ):
            #~ print "%s" % (line)
            interpret(line)
except (KeyboardInterrupt):
    # Exit with Control-C
    pass
except:
    raise
finally:
    ser.close()
