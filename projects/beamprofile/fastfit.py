from __future__ import division
import numpy as np
from scipy import optimize


def d4s(data):
    """
    Beam parameter calculation according to the ISO standard D4sigma integrals

    input: 2D array of intensity values (pixels)
    output:
    xx, yy: x and y centres
    dx, dy: 4 sigma widths for x and y
    angle: inferred rotation angle, radians
    """
    gg = data
    dimy, dimx = np.shape(data)
    X, Y = np.mgrid[0:dimx,0:dimy]
    X = X.T
    Y = Y.T
    P = np.sum(data)
    xx = np.sum(data * X) / P
    yy = np.sum(data * Y) / P
    xx2 = np.sum(data * (X - xx)**2)/P
    yy2 = np.sum(data * (Y - yy)**2)/P
    xy = np.sum(data * (X - xx) * (Y - yy)) / P
    gamm = np.sign(xx2 - yy2)
    angle = 0.5 * np.arctan(2*xy / (xx2 - yy2))
    dx = 2 * np.sqrt(2) * (xx2 + yy2 + gamm * ( (xx2 - yy2)**2 + 4*xy**2)**0.5)**(0.5)
    dy = 2 * np.sqrt(2) * (xx2 + yy2 - gamm * ( (xx2 - yy2)**2 + 4*xy**2)**0.5)**(0.5)
    return xx, yy, dx, dy, angle

def getellipse(xx, yy, dx, dy, angle):
    t = np.linspace(0, np.pi*2, 101)
    a = dx/2
    b = dy/2
    angle = np.pi + angle  # instead doing multiplication with -1 in the input
    xr = a * np.cos(t) * np.cos(angle) - b * np.sin(t) * np.sin(angle) + xx
    yr = a * np.cos(t) * np.sin(angle) + b * np.sin(t) * np.cos(angle) + yy
    return xr, yr

def gauss2d(cx, cy, sx, sy, h, X, Y):
    res = h * np.exp(-(X - cx)**2 / (2*sx**2)) * np.exp(-(Y - cy)**2 / (2*sy**2))
    return res

def waves(th, period, phase, amp, X, Y):
    pos = np.cos(th)*X + np.sin(th)*Y
    ret = np.sin(2*np.pi*pos/period + phase) * amp
    return ret

def wobble(cx, cy, sx, sy, h, th, period, phase, amp, offset):
    return lambda X, Y: gauss2d(cx, cy, sx, sy, h, X, Y) * (1 + waves(th, period, phase, amp, X, Y)) + offset

def invwobble(cx, cy, sx, sy, h, th, period, phase, amp, offset):
    return lambda X, Y: gauss2d(cx, cy, sx, sy, h, X, Y) * waves(th, period, phase, amp, X, Y) + offset

def fitwobble(data, X, Y, p0):
    """Returns (height, x, y, width_x, width_y)
    the gaussian parameters of a 2D distribution found by a fit"""
    errorfunction = lambda p: np.ravel(wobble(*p)(X, Y) - data)
    p, success = optimize.leastsq(errorfunction, p0)
    return p

if __name__ == "__main__":
    import pylab as pl

    filename = "img_343444.npy"
    # filename = "img_418733.npy"
    data = np.load(filename)

    xx, yy, dx, dy, angle = d4s(data)
    minx = max(0, int(xx-dx*0.6))
    maxx = min(640, int(xx+dx*0.6))
    miny = max(0, int(yy-dy*0.6))
    maxy = min(480, int(yy+dy*0.6))
    d2 = data[miny:maxy, minx:maxx]
    print (maxx-minx)*(maxy-miny)/(640*480)

    pl.figure()
    pl.subplot(221)
    pl.imshow(d2)
    pl.title("Original image")
    cx, cy = xx-minx, yy-miny
    sx, sy = dx / 4, dy / 4
    # sx, sy = abs(dx / 4 * np.tan(angle)),  abs(dy / 4 * np.tan(angle))
    h = np.max(d2)
    th = -60/180*np.pi
    period = 35
    phase = 4.5
    amp = 0.14
    offset = 5
    p0 = (cx, cy, sx, sy, h, th, period, phase, amp, offset)
    print p0
    dimx = maxx - minx
    dimy = maxy - miny
    X, Y = np.mgrid[0:dimx,0:dimy]
    X = X.T
    Y = Y.T
    import time
    start = time.time()
    p = fitwobble(d2, X, Y, p0)
    print time.time()-start
    cx, cy, sx, sy, h, th, period, phase, amp, offset = p
    print th, period
    w = wobble(*p0)(X, Y)
    iw = d2 - invwobble(*p)(X, Y)
    pl.subplot(222)
    pl.imshow(w)
    pl.title('fitted')

    pl.subplot(223)
    xr, yr = getellipse(cx, cy, 4*sx, 4*sy, 0)
    pl.imshow(iw)
    pl.plot(xr, yr, 'k-')
    pl.title('un-wobbled')
    pl.xlim([0, dimx])
    pl.ylim([dimy-1, 0])

    if abs(sx - sy)/(sx+sy) < 0.1:
        csign = '~'
    elif (sx > sy):
        csign = '>'
    else:
        csign = '<'
    ctext = "sx  |  sy\n%.1f %s %.1f" %(sx, csign, sy)
    pl.figtext(0.75, 0.25, ctext, horizontalalignment='center', fontsize=30)
    # pl.plot(xx, yy, '+')
    pl.show()
