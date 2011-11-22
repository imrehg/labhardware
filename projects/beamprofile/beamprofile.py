import pydc1394 as fw
from time import sleep
import numpy as np
import pylab as pl

from matplotlib import cm
from matplotlib.ticker import LinearLocator, FixedLocator, FormatStrFormatter
import matplotlib, time

if __name__ == "__main__":
    l = fw.DC1394Library()
    cams = l.enumerate_cameras()
    cam0 = fw.Camera(l, cams[0]['guid'], isospeed=800)

    print "Connected to: %s / %s" %(cam0.vendor, cam0.model)

    print "\nFeatures\n", "="*30
    for feat in cam0.features:
        print "%s : %s" %(feat, cam0.__getattribute__(feat).val)

    print cam0.modes
    cam0.mode = "640x480_Y8"  # the Y16 mode does not seem to work
    print cam0.mode


    matplotlib.interactive(True)
    fig = pl.figure()
    ax = fig.add_subplot(111)

    cam0.start(interactive=True)
    imgnum = 0
    image = None
    while True:
        try:
            # sleep(0.05)
            if image is not None:
                image.remove()
            image = ax.imshow(cam0.current_image)
            pl.draw()
            imgnum += 1
            print "Image #%d" %(imgnum)
        except KeyboardInterrupt:
            print "Stopping"
            break

    cam0.stop()
