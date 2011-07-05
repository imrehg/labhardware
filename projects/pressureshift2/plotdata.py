from numpy import *
from pylab import *
from ourgui import openFile
from sys import exit
filename = openFile(type='log')
if not filename:
    sys.exit(1)

# SetF, X, Y, BeatF 
f, x, y, b = loadtxt(filename, comments='#', delimiter=',', unpack=True)

# Check how many repetitions are there
n = 0
for res in f:
    if res == f[0]:
        n += 1
    else:
        break

points = len(f) / n;
repeats = n

## Do the averaging
xa, xe = [], []
ya, ye = [], []
ba, be = [], []
favgs = []
for i in xrange(0, points):
    try:
        ## Xaverage, Xerror
        xa.append(average(x[i*repeats:(i+1)*repeats]))
        xe.append(std(x[i*repeats:(i+1)*repeats]))
        ## Yaverage, Yerror
        ya.append(average(y[i*repeats:(i+1)*repeats]))
        ye.append(std(y[i*repeats:(i+1)*repeats]))
        ## Beataverage, Beaterror
        ba.append(average(b[i*repeats:(i+1)*repeats]))
        be.append(std(b[i*repeats:(i+1)*repeats]))
        favgs.append(f[i*repeats])
    except:
        break
favgs = array(favgs)
xa = array(xa)
xe = array(xe)
ya = array(ya)
ye = array(ye)
ba = array(ba)
be = array(be)

figure(1)
subplot(211)
plot(favgs/1e3, xa, '.')
errorbar(favgs/1e3, xa, yerr=xe, elinewidth=3, capsize=6)
xlim(f[0]/1e3,f[-1]/1e3)
xlabel('Detuning (kHz)')
ylabel('Lock-in signal (X)')
title('Fluorescence signal')

subplot(212)
plot(favgs/1e3, ba/1e3, '.')
errorbar(favgs/1e3, ba/1e3, yerr=(be/1e3), elinewidth=3, capsize=6)
xlim(favgs[0]/1e3,favgs[-1]/1e3)
xlabel('Set detuning (kHz)')
ylabel('Beat frequency (kHz)')
title('Frequency tuning check')

show()
