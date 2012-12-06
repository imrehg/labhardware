from __future__ import division
import pydc1394 as fw
from time import sleep, time, strftime
import numpy as np
import pylab as pl

from matplotlib import cm
from matplotlib.ticker import LinearLocator, FixedLocator, FormatStrFormatter
import matplotlib

import beam
import interface

if __name__ == "__main__":

    l = fw.DC1394Library()
    cams = l.enumerate_cameras()

    channel = int(raw_input("Which camera you want to use (0/1)? "))
    cam0 = fw.Camera(l, cams[channel]['guid'], isospeed=800)

    # Get number of pictures
    picnum = 1
    try:
        picnum = int(raw_input("How many pictures to take? "))
    except:
        pass

    print "Connected to: %s / %s" %(cam0.vendor, cam0.model)

    print "\nFeatures\n", "="*30
    for feat in cam0.features:
        print "%s : %s" %(feat, cam0.__getattribute__(feat).val)

    print "Camera modes:", cam0.modes
    cam0.mode = "640x480_Y8"  # the Y16 mode does not seem to work
    print "Used camera mode: %s" %(cam0.mode)
    print "Camera FPS: %.1f" %(cam0.fps)

    matplotlib.interactive(True)
    fig = pl.figure(num=1, figsize=(12.5, 12.5))

    cam0.start(interactive=True)
    imgnum = 0
    image = None
    cross = None
    pos = np.array(range(0, 640))
    ellipse = None
    fit = None    
    dimx, dimy = 640, 480
    xl = np.array(range(0, dimx))
    yl = np.array(range(0, dimy))

    timestamp = strftime("%y%m%d_%H%M%S")
    for index in range(picnum):
        data = cam0.current_image
        outname = 'beamprofile_%s_%d' %(timestamp, index)
        # save txt format for interoperation
        np.savetxt(outname+".txt", data, fmt="%d")
        interface.createiface(data)
        pl.title(outname)
        pl.savefig("%s.png" %outname)
    pl.draw()
    cam0.stop()

    pl.show()
