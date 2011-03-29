#!/usr/bin/python
import numpy as np
import pylab as pl
from ourgui import openFile

def plotData(filename):
    gatetime, allanvar = np.loadtxt(filename, comments="#", delimiter=",", unpack=True)
    pl.loglog(gatetime, allanvar, '.-')
    pl.xlabel("Gate time (s)")
    pl.ylabel("Allan deviation (Hz)")
    pl.show()

if __name__ == "__main__":
    filename = openFile(type='log')
    plotData(filename)
