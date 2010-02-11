from pylab import *
from numpy import loadtxt

LOGFILE = 'pump.log'
data = loadtxt(LOGFILE)

times = (data[:,0] - data[0,0]) / 60
val = data[:,1] / 10 
plot(times, val)
xlabel("Time (min)")
ylabel("Ion pump current (mA)")
show()

