from __future__ import division
import pydc1394 as fw
from time import sleep, time
import numpy as np
import pylab as pl

from matplotlib import cm
from matplotlib.ticker import LinearLocator, FixedLocator, FormatStrFormatter
import matplotlib

import fastfit
import interface2 as interface

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
    elements = None
    dimx, dimy = 640, 480
    pixelsize = 5.6

    while True:  # image collection and display
        try:
            data = cam0.current_image
            if elements is None:  # First display, set up output screen
                result = elements = interface.createiface(data)
            else:  # Every other iteration just update data
                result = interface.updateiface(data, elements)
            if result is None:
                break
            pl.draw()
        except KeyboardInterrupt:
            print "Stopping"
            break

    cam0.stop()
