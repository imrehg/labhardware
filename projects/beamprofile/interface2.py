from __future__ import division
import numpy as np
import pylab as pl
from mpl_toolkits.axes_grid1 import make_axes_locatable

import fastfit
import gaussfitter

# Set for our camera
sx, sy, pixelsize = 640, 480, 5.6

def sizetext(sx, sy):
    """
    Check if the difference between the two axes are similar or different
    Returns displayable text
    """
    if abs(sx - sy)/(sx+sy) < 0.05:
        csign = '~'
    elif (sx > sy):
        csign = '>'
    else:
        csign = '<'
    ctext = "wx  |  wy\n%.1f %s %.1f" %(sx, csign, sy)
    return ctext

def gauss(x, x0, sx, scale):
    """ Simple gaussian """
    return np.exp(-(x-x0)**2 / (2 * sx**2)) * scale

def analyze(data):
    """ Do all the analysis that's needed to create the interface """
    xx, yy, dx, dy, angle = fastfit.d4s(data)
    try:
        inparams = [0, np.max(data), xx, yy, dx/4, dy/4, (angle-np.pi)/np.pi*180]
        outparams = gaussfitter.gaussfit(data, params=inparams)
        b, a, xx, yy, ddx, ddy, rot = outparams
        dx = 4*ddx
        dy = 4*ddy
        angle = rot/180*np.pi+np.pi/2
        print "Gaussian fit"
    except (ValueError):
        print "D4s fit"
        pass
    xr, yr = fastfit.getellipse(xx, yy, dx, dy, angle)
    # fix axes calculation so no more -1 is needed
    angle *= -1
    adeg = "%.1f deg" %(angle / np.pi * 180)
    xxx = [xx - dx/2*np.cos(angle), xx + dx/2*np.cos(angle)]
    xxy = [yy + dx/2*np.sin(angle), yy - dx/2*np.sin(angle)]
    yyx = [xx + dy/2*np.sin(angle), xx - dy/2*np.sin(angle)]
    yyy = [yy + dy/2*np.cos(angle), yy - dy/2*np.cos(angle)]
    xwidth = (dx*np.cos(angle)**2 + dy*np.sin(angle)**2)/4.0
    ywidth = (dx*np.sin(angle)**2 + dy*np.cos(angle)**2)/4.0

    try:
        xc = int(np.round(xx))
        yc = int(np.round(yy))
    except ValueError:
        xc = 320
        yc = 240
    xcut = data[yc, :]
    ycut = data[:, xc]
    xline = range(0, sx)
    yline = range(0, sy)
    xcutg = gauss(xline, xx, xwidth, max(xcut))
    ycutg = gauss(yline, yy, ywidth, max(ycut))

    return (xx, yy, dx, dy, angle, xr, yr, adeg, xxx, xxy, yyx, yyy, xwidth, ywidth, xc, yc, xcut, ycut, xcutg, ycutg)

def createiface(data):
    (xx, yy, dx, dy, angle, xr, yr, adeg, xxx, xxy, yyx, yyy, xwidth, ywidth, xc, yc, xcut, ycut, xcutg, ycutg) = analyze(data)

    st = sizetext(dx/2*pixelsize, dy/2*pixelsize)
    text = "Data range: %d - %d" %(np.min(data), np.max(data))

    fs = 12.5
    fig = pl.figure(num=1, figsize=(fs, fs))

    axImg = pl.subplot(111)
    img = axImg.imshow(data, vmin=0, vmax=256, cmap='Paired')
    centre, = axImg.plot(xx, yy, '+', markersize=10)
    ellipse, = axImg.plot(xr, yr, 'k-', linewidth=3)
    ax1, ax2, = axImg.plot(xxx, xxy, 'k-', yyx, yyy, 'k-', linewidth=2)

    divider = make_axes_locatable(axImg)

    xline = range(0, sx)
    yline = range(0, sy)

    cutlinewidth=3
    axCuty = divider.append_axes("right", size=1.4, pad=0.1, sharey=axImg)
    yg, = axCuty.plot(ycutg, yline, 'r-', linewidth=cutlinewidth)
    yl, = axCuty.plot(ycut, yline, 'k-', linewidth=cutlinewidth)

    axCutx = divider.append_axes("bottom", size=1.4, pad=0.1, sharex=axImg)
    xg, = axCutx.plot(xline, xcutg, 'r-', linewidth=cutlinewidth)
    xl, = axCutx.plot(xline, xcut, 'k-', linewidth=cutlinewidth)

    # Setting up limits
    axImg.set_xlim([0, sx])
    axImg.set_ylim([sy, 0])
    axImg.set_xticks([])
    axImg.set_yticks([])

    axCuty.set_xlim([-10, 256])
    axCuty.set_xticks([0, 128, 256])

    axCutx.set_ylim([256, -10])
    axCutx.set_yticks([0, 128, 256])

    htext = fig.text(0.5, 0.965, 'wx/wy = Gaussian beam width (um) along principal axes (Gaussian*pixelsize)', horizontalalignment='center', fontsize=20)
    sztext = fig.text(0.5, 0.81, st, horizontalalignment='center', fontsize=67)
    atext = fig.text(0.5, 0.10, adeg, horizontalalignment='center', fontsize=65)
    uptext = fig.text(0.5, 0.05, text, horizontalalignment='center', fontsize=25)

    ret = (fig, img, centre, ellipse, ax1, ax2, xl, xg, yl, yg, sztext, uptext, atext)
    return ret

def updateiface(data, elements):
    """ 
    Run only updates of data on the interface
    
    data : input data
    elements : output of createiface(data)
    """
    (xx, yy, dx, dy, angle, xr, yr, adeg, xxx, xxy, yyx, yyy, xwidth, ywidth, xc, yc, xcut, ycut, xcutg, ycutg) = analyze(data)
    (fig, img, centre, ellipse, ax1, ax2, xl, xg, yl, yg, sztext, uptext, atext) = elements
    xline = range(0, sx)
    yline = range(0, sy)

    img.set_data(data)
    centre.set_xdata(xx)
    centre.set_ydata(yy)

    ellipse.set_xdata(xr)
    ellipse.set_ydata(yr)
    ax1.set_xdata(xxx)
    ax1.set_ydata(xxy)
    ax2.set_xdata(yyx)
    ax2.set_ydata(yyy)

    xl.set_ydata(xcut)
    xg.set_ydata(xcutg)

    yl.set_xdata(ycut)
    yg.set_xdata(ycutg)

    st = sizetext(dx/2*pixelsize, dy/2*pixelsize)
    text = "Data range: %d - %d" %(np.min(data), np.max(data))

    uptext.set_text(text)
    sztext.set_text(st)
    atext.set_text(adeg)
    

if __name__ == "__main__":
    filename = "test.txt"
    data = np.loadtxt(filename)

    elements = createiface(data)
    updateiface(data, elements)

    pl.show()
