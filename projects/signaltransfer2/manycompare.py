import numpy as np
import pylab as pl
import sys
sys.path.append('../../lablib')
import ourgui


filenames = []

while True:
    filename = ourgui.openFile()
    if filename:
        filenames += [filename]
    else:
        break

maxrange = -1
for f in filenames:
    name = f.split('\\')[-1]
    data = np.loadtxt(f, delimiter=',')
    pl.plot(data[:,0], data[:,1], label=name)
    datax = np.max(data[:, 0])
    if datax > maxrange:
        maxrange = datax

pl.xlabel('Frequency (Hz)')
pl.ylabel('Log Mag')
pl.legend(loc='best')
pl.xlim([0, maxrange])
pl.show()
