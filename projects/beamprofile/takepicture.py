from __future__ import division
import pydc1394 as fw
from time import sleep, time, strftime
import numpy as np
import pylab as pl

from matplotlib import cm
from matplotlib.ticker import LinearLocator, FixedLocator, FormatStrFormatter
import matplotlib

import beam

if __name__ == "__main__":
    l = fw.DC1394Library()
    cams = l.enumerate_cameras()
    cam0 = fw.Camera(l, cams[0]['guid'], isospeed=800)

    print "Connected to: %s / %s" %(cam0.vendor, cam0.model)

    print "\nFeatures\n", "="*30
    for feat in cam0.features:
        print "%s : %s" %(feat, cam0.__getattribute__(feat).val)

    print "Camera modes:", cam0.modes
    cam0.mode = "640x480_Y8"  # the Y16 mode does not seem to work
    print "Used camera mode: %s" %(cam0.mode)
    print "Camera FPS: %.1f" %(cam0.fps)

    matplotlib.interactive(True)
    fig = pl.figure(num=1, figsize=(10, 10))
    ax = fig.add_subplot(111)

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

    data = cam0.current_image

    stamp = strftime("%y%m%d_%H%M%S")
    outname = 'beamprofile_%s' %(stamp)
    # save txt format for interoperation
    np.savetxt(outname+".txt", data, fmt="%d")

    image = ax.imshow(data, vmin=0, vmax=256)
    pl.xlabel('x')
    pl.ylabel('y')
    pl.title(outname)

    pl.savefig("%s.png" %outname)
    pl.draw()
    cam0.stop()

    pl.show()
