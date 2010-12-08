from numpy import *
from pylab import *
from ourgui import openFile

filename = openFile(type='log')

pzt, f, v = loadtxt(filename, comments='#', delimiter=',', unpack=True)

meanf = mean(f)

figure(1)
plot(f-meanf, v, '.')
xlabel('Detuning (MHz)')
ylabel('PMT signal (V)')
show()
