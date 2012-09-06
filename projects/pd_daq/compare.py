import numpy as np
import scipy as sp
import pylab as pl
import sys
sys.path.append('../../lablib')
import ourgui


fftfile = ourgui.openFile()
sigfile = ourgui.openFile()


fftdata = np.load(fftfile)
sigdata = np.loadtxt(sigfile, delimiter=',')

freq = fftdata[:, 0]
spmag = np.log(fftdata[:, 1])

freqs = sigdata[:,0]
mags = sigdata[:,1]


pl.plot(freq, spmag-70)
pl.plot(freqs, mags)

pl.xlim([0, 6250])

pl.show()
