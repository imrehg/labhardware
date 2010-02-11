#!/usr/bin/env python

# Simple data file plotting

from pylab import *
from numpy import loadtxt

LOGFILE = 'pump.log'
data = loadtxt(LOGFILE)

# Time since start in hours
times = (data[:,0] - data[0,0]) / 60 / 60

# Ion pump back panel monitor (x10 signal amplification)
# With amp, 10V = 1mA
val = data[:,1] / 10 

plot(times, val)
xlabel("Time (h)")
ylabel("Ion pump current (mA)")
show()
