from numpy import *
from pylab import *
from ourgui import openFile

filename = openFile(type='log')

f0 = 9192631770
f, trans, fluo = loadtxt(filename, comments='#', delimiter=',', unpack=True)

f = f - f0

# Check how many repetitions are there
n = 0
for res in f:
    if res == f[0]:
        n += 1
    else:
        break

points = len(f) / n;
repeats = n

transavg = []
transerr = []
fluoavg = []
fluoerr = []
ratioavg = []
ratioerr = []
favgs = []
for i in xrange(0, points):
    try:
        transavg.append(average(trans[i*repeats:(i+1)*repeats]))
        transerr.append(std(trans[i*repeats:(i+1)*repeats]))
        fluoavg.append(average(fluo[i*repeats:(i+1)*repeats]))
        fluoerr.append(std(fluo[i*repeats:(i+1)*repeats]))
        ratioavg.append(average(fluo[i*repeats:(i+1)*repeats]/trans[i*repeats:(i+1)*repeats]))
        ratioerr.append(std(fluo[i*repeats:(i+1)*repeats]/trans[i*repeats:(i+1)*repeats]))
        favgs.append(f[i*repeats])
        # figure(10+i)
        # hist(r[i*repeats:(i+1)*repeats], bins=20)
    except:
        break



figure(1)
subplot('211')
tyscale = mean(transavg)
plot(f, trans/tyscale, '.')
errorbar(favgs, transavg/tyscale, yerr=transerr/tyscale, elinewidth=4, capsize=6)
xlabel('Detuning (Hz)')
ylabel('Transmitted light')
xlim([min(favgs), max(favgs)])

subplot('212')
fyscale = mean(fluoavg)
plot(f, fluo/fyscale, '.')
errorbar(favgs, fluoavg/fyscale, yerr=fluoerr/fyscale, elinewidth=4, capsize=6)
xlabel('Detuning (Hz)')
ylabel('Fluorescence')
xlim([min(favgs), max(favgs)])

figure(2)
plot(f, fluo/trans, '.')
errorbar(favgs, ratioavg, yerr=ratioerr, elinewidth=4, capsize=6)
xlabel('Detuning (Hz)')
ylabel('Signal ratio')
xlim([favgs[0], favgs[-1]])

show()
