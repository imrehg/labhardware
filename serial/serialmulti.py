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
from numpy import NaN

class Multimeter:

    def __init__(self):
        """ Setting up connection """
        self.ser = serial.Serial('/dev/ttyUSB0',baudrate=600, bytesize=7, stopbits=2, \
                 parity=serial.PARITY_NONE, timeout=1, xonxoff=1, rtscts=0, dsrdtr=1)
        # Needs the many DTR/RTS things for some reason
        self.ser.setDTR(1)
        self.ser.setRTS(0)
        self.ser.setDTR(1)
        self.ser.setRTS(0)
        self.ser.setDTR(1)
        self.ser.setRTS(0)
        self.ser.setDTR(1)
        self.ser.setRTS(0)
        self.pattern = re.compile(r".*(?P<mode>OH)\s*(?P<value>[\d.]*)\s*(?P<unit>[a-zA-Z]*)")

        
    def interpret(self, mode, value, unit):
        if  (re.match('O.L',value)):
            value = NaN

        value = float(value)
        if (mode == 'OH'):
            if unit == "kOhm":
                value *= 1000
            elif unit == "MOhm":
                valiue *= 1000000
            unit = "Ohm"

        return (value, unit)

        # elif (mode == 'DC'):
        #     if (re.search('V',unit)):
        #         print "DC Voltage: %s %s" % (value, unit)
        #     if (re.search('A',unit)):
        #         print "DC Current: %s %s" % (value, unit)
        # elif (mode == 'AC'):
        #     if (re.search('V',unit)):
        #         print "AC Voltage: %s %s" % (value, unit)
        #     if (re.search('A',unit)):
        #         print "AC Current: %s %s" % (value, unit)

    def ask(self):
        self.ser.write("D")
        line = self.ser.readline()
        data = self.pattern.match(line)
        if data:
            result = self.interpret(data.group('mode'), data.group('value'), data.group('unit'))
        else:
            result = None
        return result

    def close(self):
        self.ser.close()
