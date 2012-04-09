from __future__ import division
import matplotlib
matplotlib.rcParams['backend'] = 'wx'
import matplotlib.pylab as pl
import numpy as np
import scipy.optimize as op

import ourgui

if __name__ == "__main__":
    filename = ourgui.openFile("log")
    data = np.loadtxt(filename, delimiter=",", comments="#")

    f = data[:, 0]
    amp = np.abs(data[:, 1])
    ampr = amp / amp[0]
    ampdb = 20 * np.log10(ampr)

    phase = data[:, 3]
    phase = np.array([p if p < 0 else p-np.pi for p in phase])/np.pi * 180
    phase = phase - phase[0]
    
    pl.subplot(211)
    pl.semilogx(f, ampdb, 'k-')
    pl.semilogx(f, np.zeros(len(f))-3, 'r--', label='-3dB line')
    pl.xlabel("Frequency (Hz)")
    pl.ylabel("Amplitude (dB)")
    pl.title("PZT transfer function")
    pl.legend(loc='best')

    pl.subplot(212)
    pl.semilogx(f, phase, 'k-')
    pl.semilogx(f, np.zeros(len(f))-90, 'r--', label='-90deg line')
    pl.ylabel("Phase (deg)")
    pl.xlabel("Frequency (Hz)")
    pl.ylim([np.min(phase)-20, np.max(phase)+20])
    pl.legend(loc='best')

    pl.show()

