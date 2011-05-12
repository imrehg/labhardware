from numpy import *
from pylab import *
from ourgui import openFile

filename = openFile(type='log')

f0 = 9192631770
f, ch1, ch2 = loadtxt(filename, comments='#', delimiter=',', unpack=True)

# Turn into MHz
f = f / 1e6

# Check how many repetitions are there
n = 0
for res in f:
    if res == f[0]:
        n += 1
    else:
        break

points = len(f) / n;
repeats = n

ch1avg = []
ch1err = []
ch2avg = []
ch2err = []
favgs = []
for i in xrange(0, points):
    try:
        ch1avg.append(average(ch1[i*repeats:(i+1)*repeats]))
        ch1err.append(std(ch1[i*repeats:(i+1)*repeats]))
        ch2avg.append(average(ch2[i*repeats:(i+1)*repeats]))
        ch2err.append(std(ch2[i*repeats:(i+1)*repeats]))
        favgs.append(f[i*repeats])
    except:
        break

figure(1)
subplot('211')
plot(f, ch1, '.')
errorbar(favgs, ch1avg, yerr=ch1err, elinewidth=4, capsize=6)
xlabel('Detuning (MHz)')
ylabel('Channel 1')
xlim([min(favgs), max(favgs)])

subplot('212')
plot(f, ch2, '.')
errorbar(favgs, ch2avg, yerr=ch2err, elinewidth=4, capsize=6)
xlabel('Detuning (MHz)')
ylabel('Channel 2')
xlim([min(favgs), max(favgs)])

show()
