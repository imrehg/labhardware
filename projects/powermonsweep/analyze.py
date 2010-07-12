

from __future__ import division
from numpy import *
from pylab import *
from ourgui import openFile


filename = openFile(type='log')
#filename = "pressureshift_100712_184902.log"
f, p = loadtxt(filename, comments='#', delimiter=',', unpack=True)

# Check how many repetitions are there
n = 0
for res in f:
    if res == f[0]:
        n += 1
    else:
        break

points = int(len(f) / n);
repeats = n


avgs = []
errbar = []
favgs = []
for i in xrange(0, points):
    try:
        avgs.append(average(p[i*repeats:(i+1)*repeats]))
        errbar.append(std(p[i*repeats:(i+1)*repeats])/sqrt(repeats))
#        errbar.append(std(p[i*repeats:(i+1)*repeats]))
        favgs.append(f[i*repeats])
    except:
        break
favgs = array(favgs)/1e6
errbar = array(errbar)*1e3
avgs = array(avgs)*1e3

out = zip(favgs, avgs, errbar)
savetxt(filename+".sum",out)

errorbar(favgs, avgs, errbar, fmt='.')
xlabel("Detuning (MHz)")
ylabel("Average power (mW)")
show()

