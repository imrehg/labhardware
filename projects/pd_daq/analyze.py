import numpy as np
import scipy as sp
import pylab as pl
import sys
sys.path.append('../../lablib')
import ourgui

filename = ourgui.openFile()
meas = np.loadtxt(filename, comments='#')
n = len(meas)
rate = 20000.0
totalt = n / rate
t = np.linspace(0, totalt, n)

pl.subplot(211)
pl.plot(t, meas)

dt = t[1]-t[0]
freq = np.fft.fftfreq(t.shape[-1], d=dt)
print max(freq)
sp = np.fft.fft(meas)
spmag = np.sqrt(sp.real**2 + sp.imag**2)
spmag = spmag[freq >= 0]
freq = freq[freq >= 0]
print spmag
pl.subplot(212)
pl.semilogy(freq, spmag)
pl.xlim([0, 6250])

out = zip(freq, spmag)
np.save(filename+'.fft', out)

pl.show()
