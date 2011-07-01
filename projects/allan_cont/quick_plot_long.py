#!/usr/bin/python
import numpy as np
import pylab as pl
from ourgui import openFile

def plotData(filename):
    frequency = np.loadtxt(filename, comments="#", delimiter=",", unpack=True)
    meanfreq = np.mean(frequency)
    freq = frequency - meanfreq
    std = np.std(freq)
    pl.plot(freq, '.')
    pl.xlabel("Datapoints")
    pl.ylabel("Frequency deviation (Hz)")
    pl.title("Average frequency: %.5fHz +- %.5fHz" %(meanfreq, std))
    pl.show()

if __name__ == "__main__":
    filename = openFile(type='log')
    plotData(filename)
