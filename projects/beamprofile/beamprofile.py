from __future__ import division
import pydc1394 as fw
from time import sleep, time
import numpy as np
import pylab as pl

from matplotlib import cm
from matplotlib.ticker import LinearLocator, FixedLocator, FormatStrFormatter
import matplotlib

import fastfit

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

if __name__ == "__main__":
    l = fw.DC1394Library()
    cams = l.enumerate_cameras()
    cam0 = fw.Camera(l, cams[0]['guid'], isospeed=800)

    print "Connected to: %s / %s" %(cam0.vendor, cam0.model)

    # Settings
    cam0.framerate.mode = 'manual'
    cam0.framerate.val = 25
    cam0.exposure.mode = 'manual'
    cam0.exposure.val = cam0.exposure.range[0]
    cam0.shutter.mode = 'manual'
    print cam0.shutter.range
    print cam0.exposure.range
    cam0.shutter.val = cam0.shutter.range[0]

    print "\nFeatures\n", "="*30
    for feat in cam0.features:
        try:
            val = cam0.__getattribute__(feat).val
        except:
            val = '??'
        try:
            mode = cam0.__getattribute__(feat).mode
        except:
            mode = '??'

        print "%s : %s (mode: %s)" %(feat, val, mode)

    print "Camera modes:", cam0.modes
    cam0.mode = "640x480_Y8"  # the Y16 mode does not seem to work
    print "Used camera mode: %s" %(cam0.mode)

    matplotlib.interactive(True)
    fs = 12.5
    fig = pl.figure(num=1, figsize=(fs, fs))
    ax = fig.add_subplot(111)

    cam0.start(interactive=True)
    image = None
    dimx, dimy = 640, 480
    pixelsize = 5.6

    while True:  # image collection and display
        try:
            data = cam0.current_image
            text = "Data range: %d - %d" %(np.min(data), np.max(data))
            xx, yy, dx, dy, angle = fastfit.d4s(data)
            adeg = "%.1f deg" %(-angle / np.pi * 180)
            xr, yr = fastfit.getellipse(xx, yy, dx, dy, angle)
            xxx = [xx - dx/2*np.cos(angle), xx + dx/2*np.cos(angle)]
            xxy = [yy + dx/2*np.sin(angle), yy - dx/2*np.sin(angle)]
            yyx = [xx + dy/2*np.sin(angle), xx - dy/2*np.sin(angle)]
            yyy = [yy + dy/2*np.cos(angle), yy - dy/2*np.cos(angle)]

            st = sizetext(dx/2*pixelsize, dy/2*pixelsize)

            if image is None:  # First display, set up output screen
                # the data
                image = ax.imshow(data, vmin=0, vmax=255, cmap='Paired')

                # extra display: centre marker, D4s ellipse, axes
                centre, = ax.plot(xx, yy, '+', markersize=10)
                ellipse, = ax.plot(xr, yr, 'k-', linewidth=3)
                ax1, ax2, = ax.plot(xxx, xxy, 'k-', yyx, yyy, 'k-', linewidth=2)

                # reposition picture, since plot ruins imshow's limits
                centre.axes.set_xlim([0, dimx])
                centre.axes.set_ylim([dimy-1, 0])

                # Data headers
                sztext = fig.text(0.5, 0.965, 'wx/wy = Gaussian beam width (um) along principal axes (D4s/2*pixelsize)', horizontalalignment='center', fontsize=20)
                sztext = fig.text(0.5, 0.81, st, horizontalalignment='center', fontsize=67)
                atext = fig.text(0.5, 0.10, adeg, horizontalalignment='center', fontsize=65)
                uptext = fig.text(0.5, 0.05, text, horizontalalignment='center', fontsize=25)
                # np.save('test', data)
            else:  # Every other iteration just update data
                image.set_data(data)

                centre.set_xdata(xx)
                centre.set_ydata(yy)

                ellipse.set_xdata(xr)
                ellipse.set_ydata(yr)
                ax1.set_xdata(xxx)
                ax1.set_ydata(xxy)
                ax2.set_xdata(yyx)
                ax2.set_ydata(yyy)

                uptext.set_text(text)
                sztext.set_text(st)
                atext.set_text(adeg)
            pl.draw()
        except KeyboardInterrupt:
            print "Stopping"
            break

    cam0.stop()
