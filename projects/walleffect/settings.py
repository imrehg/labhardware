#!/usr/bin/env python

# Wall effect measurement control code
# Test routines

import transstage
from numpy.random import uniform
from time import sleep

cont = transstage.MotorControl('/dev/ttyUSB0')

def getsettings(cont):
    print "Current settings -----"
    print "P-term : %s"%(cont.command("GP").strip())
    print "D-term : %s"%(cont.command("GD").strip())
    print "I-term : %s"%(cont.command("GI").strip())
    print "I-limit: %s"%(cont.command("GL").strip())
    print "Accel  : %s"%(cont.command("TL").strip())
    print "Veloc  : %s"%(cont.command("TY").strip())
    print "----------------------"

def setsettings(cont, (dp, dd, di, dl, sa, sv)):
    cont.command("DP%d"%(dp))
    cont.command("DD%d"%(dd))
    cont.command("DI%d"%(di))
    cont.command("DL%d"%(dl))
    cont.command("SA%d"%(sa))
    cont.command("SV%d"%(sv))

def gostep(step):
    print step
    cont.command("MR%d"%(step))
    sleep(1)
    print "----------------------"
    print "Target   : %s"%(cont.command("TT").strip())
    print "Position : %s"%(cont.command("TP").strip())
    print "Error    : %s"%(cont.command("TE").strip())

def randompos(step):
    if (uniform() < 0.5):
        step = -step
    gostep(step)

## Reset the controller
# cont.command("RT")
# sleep(5)

## Update settings
# Settings from the manual
#set = (120, 20, 150, 2000, 1000000, 180000)
# Safer settings
#set = (120, 20, 150, 2000, 10000, 18000)
#setsettings(cont, set)
getsettings(cont)

print "Position: %d" %(cont.getposition())

## Random Move
# step = 1000
# for i in range(6):
#     randompos(step)

## Normal move
cont.command("MA0")
cont.command("MR1000")

## Read status and error messages
cont.getstatus()

## Final reading
sleep(1)
print "Position: %s" %(cont.command("TP"))
print "Target  : %s" %(cont.command("TT"))
