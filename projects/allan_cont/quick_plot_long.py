#!/usr/bin/python
import numpy as np
import pylab as pl
from ourgui import openFile

def plotData(filename):
    time, frequency = np.loadtxt(filename, comments="#", delimiter=",", unpack=True)
    time -= time[0]
    meanfreq = np.mean(frequency)
    freq = frequency - meanfreq
    std = np.std(freq)
    pl.plot(time, frequency, '.')
    pl.xlabel("Time since start")
    pl.ylabel("Frequency deviation")
    pl.title("Average frequency: %.5%, std: %.5f" %(meanfreq, std))
    pl.show()

if __name__ == "__main__":
    filename = openFile(type='log')
    plotData(filename)
