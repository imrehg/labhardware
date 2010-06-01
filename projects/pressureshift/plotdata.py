from numpy import *
from pylab import *
from ourgui import openFile

filename = openFile(type='log')

f, r, th = loadtxt(filename, comments='#', delimiter=',', unpack=True)

# Check how many repetitions are there
n = 0
for res in f:
    if res == f[0]:
        n += 1
    else:
        break

points = len(f) / n;
repeats = n

avgs = []
errbar = []
favgs = []
for i in xrange(0, points):
    try:
        avgs.append(average(r[i*repeats:(i+1)*repeats]))
        errbar.append(std(r[i*repeats:(i+1)*repeats]))
        favgs.append(f[i*repeats])
    except:
        break
favgs = array(favgs)

figure(1)
subplot('211')
plot(f/1e3, r, '.')
errorbar(favgs/1e3, avgs, yerr=errbar, elinewidth=3, capsize=6)
xlim(f[0]/1e3,f[-1]/1e3)
xlabel('Detuning (kHz)')
ylabel('Lock-in signal')
subplot('212')
plot(f/1e3, th/180, '.')
xlim(f[0]/1e3,f[-1]/1e3)
xlabel('Detuning (kHz)')
ylabel('Phase')
show()
