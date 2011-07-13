import numpy as np
import pylab as pl
from ourgui import openFile

def plotline(maxx, minx=0, value=0, style="k-", plotfunc=pl.plot):
    plotfunc([minx, maxx], [value, value], style)

def quickplot(filename):
    data = np.loadtxt(filename, comments="#")
    maxdata, mindata, stddata, meandata = np.max(data), np.min(data), np.std(data), np.mean(data)

    n = len(data)
    pl.subplot(211)
    pl.plot(data,'k.')
    plotline(n, value=maxdata, style="g-")
    plotline(n, value=mindata, style="r-")
    plotline(n, value=meandata, style="k-")
    plotline(n, value=(meandata+stddata), style="b-")
    plotline(n, value=(meandata-stddata), style="b-")

    pl.xlabel('data points')
    pl.ylabel('voltage (V)')
    pl.title("Voltage: %f (+- %f) V" %(meandata, stddata))

    pl.subplot(212)
    n, bins, patches = pl.hist(data, 100, normed=1, facecolor='green', alpha=0.75)
    pl.xlabel('voltage')
    pl.ylabel('distribution')

    pl.show()

filename = openFile("log")
if filename:
    quickplot(filename)
