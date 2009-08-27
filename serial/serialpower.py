#!/usr/bin/env python

# RS-232 serial support for Newport Optical Power Meter 1830-C
# Find all codes in manual!
# Very simple example code: reading current value and displaying in terminal

import serial

ser = serial.Serial('/dev/ttyUSB0',baudrate=9600, bytesize=8, stopbits=1, \
    parity=serial.PARITY_NONE, timeout=2, xonxoff=1)

try:
    while True:
        ser.write("D?\n")
        line = ser.readline().strip()
        print "%s" % (line)
except (KeyboardInterrupt):
    # Exit with Control-C
    pass
except:
    raise
finally:
    ser.close()
