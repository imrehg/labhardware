import numpy as np
import pylab as pl
from ourgui import openFile

def plotline(maxx, minx=0, value=0, style="k-", plotfunc=pl.plot):
    plotfunc([minx, maxx], [value, value], style)

def quickplot(filename):
    alldata = np.loadtxt(filename, comments="#", delimiter=",")
    datashape = np.shape(alldata)
    try:
        col = np.shape(alldata)[1]
        data = alldata[:, col-1]
    except (IndexError):
        data = alldata

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
    pl.ylabel('Frequency (Hz)')
    pl.title("Frequency: %f (+- %f) Hz" %(meandata, stddata))

    pl.subplot(212)
    n, bins, patches = pl.hist(data-meandata, 100, normed=1, facecolor='green', alpha=0.75)
    pl.xlabel('Frequency deviation from mean (Hz)')
    pl.ylabel('distribution')

    pl.show()

filename = openFile("log")
if filename:
    quickplot(filename)
