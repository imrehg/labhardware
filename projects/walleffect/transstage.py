#!/usr/bin/env python

# RS-232 Serial support  for PI C-862 motor controller
#
# Based on:
# MS 74E User Manual
# C-862 Mercury DC-Motor Controller
# Release: 8.4.3 Date: 2005-10-27
"""
 List of commands:
 AB  Abort: Stop motion abruptly
 AB1 Abort: Stop motion smoothly with programmed deceleration
 BF  Set brake OFF
 BN  Set brake ON
 CA  Pulse output for PZT stages, channel A
 CB  Pulse output for PZT stages, channel B
 CF  Channel OFF
 CN  Channel ON
 CP  Channel pattern
 CS  Report checksum
 DD  Define d-term (derivative gain)
 DH  Define home
 DI  Define i-term (integral gain)
 DL  Define integration limit
 DP  Define p-term (proportional gain)
 EF  Set Echo OFF
 EM  Execute Macro
 EN  Set Echo ON
 FE  Find edge (find origin position )
 GD  Get d-term
 GH  Go home
 GI  Get i-term
 GL  Get integration limit
 GP  Get p-term
 LF  Limit switch operation OFF
 LH  Limit switches active high
 LL  Limits switches active low
 LN  Limit switch operation ON
 MA  Move absolute
 MD  Macro definition
 MF  Motor off
 MN  Motor on
 MR  Move relative
 RM  Reset (erase) macro
 RP  Repeat from beginning of line
 RT  Reset (like power-on reset)
 SA  Set Acceleration
 SC  Select controller
 SM  Set maximum following error
 ST  Stop motion smoothly and move back
 SV  Set Velocity
 TA  Tell analog input value
 TB  Tell board address
 TC  Tell channel (digital input)
 TD  Tell dynamic target
 TE  Tell error (distance from target)
 TF  Tell profile following error
 TI  Tell iteration number
 TL  Tell programmed acceleration
 TM  Tell macro contents
 TP  Tell position
 TS  Tell status
 TT  Tell target position
 TV  Tell actual velocity
 TY  Tell programmed velocity
 TZ  Tell Macro Zero
 UD  Update flash
 VE  Display version number
 WA  Wait absolute time
 WF  Wait channel OFF
 WN  Wait channel ON
 WS  Wait stop
 XF  Execute if channel OFF
 XN  Execute if channel ON
 '   Single Character Command: TP (Tell Position)
 #   Single Character Command: TC (Tell Channel)
 %   Single Character Command: TS (Tell Status)
 ?   Single Character Command: TE (Tell Position Error)
 (   Single Character Command: TF (Tell Profile Error)
 /   Single Character Command: (Tell LM629 status)
 !   Single Character Command: Halt for all members
"""

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


