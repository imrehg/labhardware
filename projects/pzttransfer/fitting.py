from __future__ import division
import matplotlib
matplotlib.rcParams['backend'] = 'wx'
import matplotlib.pylab as pl
import numpy as np
import scipy.optimize as op

def dofit(freq, t, v, periods=1):
    """ Fit a sine wave with a given frequency to the data """

    t = t[t < periods/freq]
    v = v[0:len(t)]

    fitfunc = lambda p, x: p[0]*np.sin(2*np.pi*freq*x+p[1]) + p[2] # Target function
    errfunc = lambda p, x, y: fitfunc(p, x) - y # Distance to the target function
    p0 = [(np.max(v)-np.min(v))/2, 0, np.mean(v)] # Initial guess for the parameters
    p1, success = op.leastsq(errfunc, p0[:], args=(t, v))
    vf = fitfunc(p1, t)
    return p1, lambda t: fitfunc(p1, t)


if __name__ == "__main__":
    freq = 1000
    data = np.loadtxt("test")
    t = data[:, 0]
    v = data[:, 1]

    p, vf = dofit(freq, t, v)
    print "Amplitude:", p[0]
    print "Phase:", p[1]
    pl.subplot(211)
    pl.plot(t, v)
    pl.plot(t, vf(t))

    pl.subplot(212)
    pl.plot(t, v-vf(t))

    pl.show()

