from numpy import loadtxt, sqrt
from pylab import plot, show, subplot, xlabel, ylabel, title
from ourgui import openFile

def quickplot(filename):
    data = loadtxt(filename, skiprows=1)
    t = data[:,0]
    orig = 2.5
    scale = 1
    v1 = (data[:,1] - orig) / scale
    v2 = (data[:,2] - orig) / scale
    v3 = (data[:,3] - orig) / scale
    vabs = sqrt(v1**2 + v2**2 + v3**2)

    subplot(2,2,1)
    plot(t*1000,v1,'.')
    xlabel('time (ms)')
    ylabel('Magnetic field (G)')
    title('Axis')

    subplot(2,2,2)
    plot(t*1000,v2,'.')
    xlabel('time (ms)')
    ylabel('Magnetic field (G)')
    title('Y axis')

    subplot(2,2,3)
    plot(t*1000,v3,'.')
    xlabel('time (ms)')
    ylabel('Magnetic field (G)')
    title('Z axis')
    
    subplot(2,2,4)
    plot(t*1000,vabs,'.')
    xlabel('time (ms)')
    ylabel('Magnetic field (G)')
    title('Absolute magnetic field')
    show()

filename = openFile("log")
if filename:
    quickplot(filename)
