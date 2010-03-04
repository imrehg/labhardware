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

class MotorControl:
    """ C-862 DC Motor controller
    """

    def __init__(self, serialport, baudrate=9600, address="0"):
        """ Create motor controller serial interface
        Input:
        serialport : name of the serial port (eg. "/dev/ttyUSB0" or "COM1")
        baudrate=9600 : baudrate (standard: 9600, non-standard: 19200)
        address=0 : set by DIP switches (0..F hex number in ASCII)
        """
        self.iface = serial.Serial(serialport, baudrate, bytesize=8, \
                                   stopbits=1, parity=serial.PARITY_NONE, \
                                   timeout=1, xonxoff=0, rtscts=0, dsrdtr=0)
        self.setaddress(address)


    def setaddress(self, address):
        """ Set address to talk to
        Address: 0..F hex number in ASCII
        """
        self.command(chr(0x01) + address)


    def __cleanreadline(self):
        """ Read one line on the interface and clean it
        The standard reply ends with '\n\r'+ETX (end-of-text, 0x03),
        which should be removed.
        """
        return self.iface.readline().strip('\r\n'+chr(0x03))
	      
    def command(self, command, lines_num=1):
        """ Send command to controller, and read answer if there's any
        For correct behaviour, it seems we have to read at least one line
        """
        self.iface.write(command+"\r")
        read = ""
        for i in range(lines_num):
            read += self.__cleanreadline()
            # print command+">>"+str(len(read))+">"+read+"<"
            if i < (lines_num - 1):
                 read += "\n"
        return(read)

    def getposition(self):
        """ Return current position
        """
        reply = self.command("TP", 1).strip()
        pos = int(reply[2:])
        return(pos)

    def definehome(self):
        """ Define current position as 'home', i.e. position 0
        """
        self.command("DH")

    def moveabs(self, counts):
        """ Move to absolute position defined by 'counts'
        +/- direction, -: in, +: out
        """
        self.command("MA%d"%(counts))

    def moverel(self, counts):
        """ Move to absolute position defined by 'counts'
        +/- direction, -: in, +: out
        """
        self.command("MR%d"%(counts))

    def setvelocity(self, velocity):
        self.command("SV%d"%(velocity))

    def setmaxerror(self, maxerror):
        """ Set maximum following error
        If set to too low level, stage won't move
        """
        if (maxerror < 400):
            maxerror = 400
        self.command("SM%d"%(maxerror))

    def __bincheck(self, a, b):
        if (int(a, 16) & (2 ** b)):
            return(1)
        else:
            return(0)

    def getstatus(self):
        """ Get and interpret status messages
        """
        status = self.command("TS")

        print "-- LM629 Status --"
        part = status[2:4]
        statmes = ["Busy", \
                   "Command  error", \
                   "Trajectory complete", \
                   "Index pulse received", \
                   "Position limit exceeded", \
                   "Excessive position error", \
                   "Breakpoint reached", \
                   "Motor Loop OFF"]
        for i in range(8):
            if (self.__bincheck(part, i)):
                print statmes[i]

        print "-- Internal operation flags --"
        part = status[5:7]
        statmes = ["Echo ON", \
                   "Wait in progress", \
                   "Command error", \
                   "Leading zero suppession active", \
                   "Macro command called", \
                   "Leading zero supression disabled", \
                   "Number mode in effect", \
                   "Board addressed"]
        for i in range(8):
            if (self.__bincheck(part, i)):
                print statmes[i]

        print "-- Motor loop flags --"
        part = status[8:10]
        statmes = ["N/A", \
                   "N/A", \
                   "Move direction polarity", \
                   "Move error (MF condition occurred in WS)", \
                   "N/A", \
                   "N/A", \
                   "Move error (Excess following error in WS)", \
                   "Internal LM629 communication in progress"]
        for i in range(8):
            if (self.__bincheck(part, i)):
                print statmes[i]

        print "-- Signal lines status --"
        part = status[11:13]
        statmes = ["Limit swith ON", \
                   "Limit switch active state HIGH", \
                   "Find edge operation in progress", \
                   "Brake ON", \
                   "N/A", \
                   "N/A", \
                   "N/A", \
                   "N/A"]
        for i in range(8):
            if (self.__bincheck(part, i)):
                print statmes[i]

        print "-- Signal input lines --"
        part = status[14:16]
        statmes = ["N/A", \
                   "Reference signal input", \
                   "Positive limit signal input", \
                   "Negative limit signal input", \
                   "N/A", \
                   "N/A", \
                   "N/A", \
                   "N/A"]
        for i in range(8):
            if (self.__bincheck(part, i)):
                print statmes[i]

        print "-- Error codes --"
        part =int(status[17:19], 16)
        statmes = ["No error", \
                   "Command not found", \
                   "First command character was not a letter", \
                   "N\A"
                   "N\A"
                   "Character following was not a digit", \
                   "Value too large", \
                   "Value too small", \
                   "Continuation character was not a comma", \
                   "Command buffer overflow", \
                   "Macro storage overflow"];
        if (part in range(10)):
            print statmes[part]

