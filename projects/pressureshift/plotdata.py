from numpy import *
from pylab import *
from ourgui import openFile

filename = openFile(type='log')

f, beat, r, th = loadtxt(filename, comments='#', delimiter=',', unpack=True)

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

plot(f, r, '.')
errorbar(favgs, avgs, yerr=errbar, elinewidth=3, capsize=6)
xlabel('Detuning (Hz)')
ylabel('Lock-in signal')
show()
