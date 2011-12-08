from __future__ import division
import pydc1394 as fw
from time import sleep, time
import numpy as np
import pylab as pl

from matplotlib import cm
from matplotlib.ticker import LinearLocator, FixedLocator, FormatStrFormatter
import matplotlib

import gaussfitter as gf

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
    ax = fig.add_subplot(211)
    sideax = fig.add_subplot(212)

    cam0.start(interactive=True)
    imgnum = 0
    image = None
    cross = None
    pos = np.array(range(0, 640))
    ellipse = None
    fit = None
    start = time()
    while True:
        try:
            data = cam0.current_image
            hline = data[280, :]
            if image is not None:
                image.set_data(data)
                cross.set_ydata(hline)
            else:
                image = ax.imshow(data)         
                cross, = sideax.plot(pos, hline, 'k-')
                cross.axes.set_ylim([0, 255])
                cross.axes.set_xlim([0, 640])
                np.save('img_%s' %(str(int(time()))[4:]), data)
            pl.draw()
            imgnum += 1
            if (imgnum % 50) == 0:
                now = time()
                print "Displayed FPS: %.2f" %(50 / (now-start))
                start = now
        except KeyboardInterrupt:
            print "Stopping"
            break

    cam0.stop()
