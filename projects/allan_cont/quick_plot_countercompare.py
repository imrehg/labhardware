#!/usr/bin/python
import numpy as np
import pylab as pl
from ourgui import openFile

counter = np.array([[1e-6, 1.1e-6],
                    [1e-5, 1.1e-7],
                    [1e-4, 1.1e-8],
                    [1e-3, 1.1e-9],
                    [1e-2, 1.1e-10],
                    [1e-1, 1.1e-11],
                    [1, 1.1e-12]])

def plotData(filename):
    data = np.loadtxt(filename, comments="#", delimiter=",", unpack=False)
    gatetime = data[:, 0]
    allanvar = data[:, 1]
    freq = data[:, 2]
    allanfraq = allanvar / freq
    pl.loglog(gatetime, allanfraq, '.-')
    
    pl.loglog(counter[:, 0], counter[:, 1], '-')
    pl.loglog(counter[:, 0], counter[:, 1]*10, '-')

    pl.xlabel("Gate time (s)")
    pl.ylabel("Allan deviation (Hz)")
    pl.xlim([min(gatetime), max(gatetime)])
    pl.show()

if __name__ == "__main__":
    filename = openFile(type='log')
    plotData(filename)
