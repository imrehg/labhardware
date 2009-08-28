#!/usr/bin/env python

# Monitoring and controlling Tektronix TDS1012B over USBTMC

from __future__ import division
import os
from time import time, sleep
import string
import re
import pylab
from scipy import *

error = False

def sendCmd(handle, cmd):
    print "Query: %s" %(cmd)
    try:
        handle.write("%s\n" %(cmd))
    except:
        error = True

def recvCmd(handle, timeout):
   starttime = time()
   while (time() - starttime) < timeout:
      try:
         handle.seek(0, 0)
         data = handle.read(2048)
         return data
         break
      except:
         continue
   return ""

#### Setup
scopedev = "/dev/usbtmc0"
handle = open(scopedev, "r+")


def loopplot(handle):
    if (not error):
        try:
            # Get voltage scale
            sendCmd(handle,"CH1:scale?")
            data = recvCmd(handle,5).strip()
            print "Reply: %s" %(data)
            vscale = float(data)

            # Get time scale
            sendCmd(handle,"HOR:scale?")
            data = recvCmd(handle,5).strip()
            print "Reply: %s" %(data)
            hscale = float(data)

            sendCmd(handle,"acquire:stopafter runstop")
            sendCmd(handle,"acquite:state run")

            sendCmd(handle,"MEASUrement:IMMed:TYPe Frequency")
            sendCmd(handle,"MEASUrement:IMMed:Value?")
            data = recvCmd(handle,5).strip()
            print "Reply: %s" %(data)
            freq = float(data)

            size=2500
            width=1
            sendCmd(handle,"data:source ch1;width %d;ENCdg RPB;stop %d" % (width,size))

            sendCmd(handle,"curve?")
            data = recvCmd(handle,5)
            dd = int(data[1])
            num = int(data[2:2+dd])
            totalnum = 2 + dd + num
            print "Number of points: %d" %(num)
            while (len(data) < totalnum):
                moredata = recvCmd(handle,5)
                if (len(moredata) > 0):
                    data += moredata
                else:
                    break
            data = data.strip()
            data = data[(totalnum-num):]
            print "Data-length: %d " % (len(data))

            out = zeros(num/width)
            if (width == 1):
                for i in range(0, len(data)):
                    out[i] = ord(data[i]) - 128
            else:
                for i in range(0, len(data), 2):
                    out[int(i/2)] = (ord(data[i])*256 + ord(data[i])) - 32768

            xlim = hscale*10;
            x = linspace(0,xlim,size) * 1000

            y = out / 128 * 5 * vscale * 1000;

            fig = pylab.figure()
            pylab.plot(x,y,'-')

            pylab.xlabel("Time (ms)")
            pylab.ylabel("Voltage (mV)")

            if (freq/1e6 > 1):
                fvalue = freq / 1e6
                funit = "MHz"
            elif (freq/1e3 > 1):
                fvalue = freq / 1e3
                funit = "kHz"
            else:
                fvalue = freq
                funit = "Hz"

            pylab.title('Measured frequency: %f %s' % (fvalue, funit))
            pylab.grid(True)

            pylab.savefig("/mnt/temp/scope.png", format="png")

        except e:
            raise e
        except (KeyboardInterrupt):
            return 101
        except:
            return 1

        return 0

while True:
    ret = loopplot(handle)
    if ret == 101:
        break
    sleep(2)

### Cleaning up
handle.close()
handle = -1
