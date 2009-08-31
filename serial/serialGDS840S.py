#!/usr/bin/env python

# RS-232 serial support for GW Instek GDS-840S Digital Storage Oscilloscope
# http://www.gwinstek.com/html/en/DownloadFile.asp?sn=255&uid=&lv=
# Filename: 82DS-82000IA.pdf

import serial

# Values set on unit manually (but these are standard settings)
ser = serial.Serial('/dev/ttyUSB0',baudrate=38400, bytesize=8, stopbits=1, \
    parity=serial.PARITY_NONE, timeout=3)

ser.open()

def sendCmd(handler,command):
    handler.write("%s\n" %(command))

def recvCmd(handler):
    return handler.readline().strip()
    
    
sendCmd(ser, "*IDN?")
id = ser.readline()
print id

#~ sendCmd(ser, ":AUToset")

sendCmd(ser, ":MEASure:FREQuency?")
freq = recvCmd(ser)
print freq

ser.close()
