#!/usr/bin/env python

# RS-232 Serial support  for PI C-862 motor controller

import serial
from time import time, sleep


# Setting up connection. Needs the many DTR/RTS things for some reason....
ser = serial.Serial('/dev/ttyUSB0',baudrate=9600, bytesize=8, stopbits=1, \
    parity=serial.PARITY_NONE, timeout=1, xonxoff=0, rtscts=0, dsrdtr=0)

def command(serial, command):
    print "Command: %s" %(command)
    serial.write(command+"\r")
    return serial.readline().strip()

def getposition(serial):
    print "Position: %s" %(command(serial,"TP"))
def getpostarget(serial):
    print "Target: %s" %(command(serial,"TT"))
def getposerror(serial):
    print "Error: %s" %(command(serial,"TE"))

def allpos(serial):
    serial.write("TT,TP,TE\r")
    tt = serial.readline().strip()
    tp = serial.readline().strip()
    te = serial.readline().strip()
    print "Target: %s" %(tt)
    print "Position: %s" %(tp)
    print "Error: %s" %(te)

def gohome(serial):
    command(serial,"GH")

def setvelocity(serial,velocity):
    command(serial,"SV%d"%(velocity))

def move(serial,distance):
    print "Move: %d" %(distance)
    command(serial,"MR%d"%(distance))


ser.write(chr(0x01)+"0")
move(ser,1000000)
#gohome(ser)

getpostarget(ser)
getposerror(ser)
setvelocity(ser, 200000)
#move(ser,-1000000)


