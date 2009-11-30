from numpy import loadtxt
from pylab import plot, show, subplot, xlabel, ylabel
from ourgui import openFile

def quickplot(filename):
    data = loadtxt(filename, skiprows=1)
    t = data[0:-1,0] - data[0,0]
    v = data[0:-1,1]
    plot(t,v,'.')
    xlabel('time (s)')
    ylabel('voltage (mV)')
    show()

filename = openFile("log")
if filename:
    quickplot(filename)
