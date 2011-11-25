import pydc1394 as fw
from time import sleep, time
import numpy as np
import pylab as pl

from matplotlib import cm
from matplotlib.ticker import LinearLocator, FixedLocator, FormatStrFormatter
import matplotlib

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
    fig = pl.figure()
    ax = fig.add_subplot(111)

    cam0.start(interactive=True)
    imgnum = 0
    image = None
    start = time()
    while True:
        try:
            if image is not None:
                image.remove()
            data = cam0.current_image
            image = ax.imshow(data)
            pl.draw()
            imgnum += 1
            # print "Image #%d" %(imgnum)
            if (imgnum % 50) == 0:
                now = time()
                print "Displayed FPS: %.2f" %(100 / (now-start))
                start = now
        except KeyboardInterrupt:
            print "Stopping"
            break

    cam0.stop()
