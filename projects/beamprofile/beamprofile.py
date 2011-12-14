from __future__ import division
import pydc1394 as fw
from time import sleep, time
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
    ax = fig.add_subplot(211)
    sideax = fig.add_subplot(212)

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
    start = time()
    while True:
        try:
            data = cam0.current_image
            xx, yy, dx, dy, angle = beam.analyze(data)
            angle = np.pi - angle
            angle = angle/2
            xcut = data[yy, :]
            ycut = data[:, xx]

            if image is not None:
                image.set_data(data)
                centre.set_ydata(yy)
                centre.set_xdata(xx)
                crossx.set_ydata(xcut)
                # xaxis.set_xdata([xx-np.cos(angle)*dx/2, xx+np.cos(angle)*dx/2])
                # xaxis.set_ydata([yy-np.sin(angle)*dx/2, yy+np.sin(angle)*dx/2])
            else:
                image = ax.imshow(data, vmin=0, vmax=256)

                # xaxis, = ax.plot([xx-np.cos(angle)*dx/2, xx+np.cos(angle)*dx/2], [yy-np.sin(angle)*dx/2, yy+np.sin(angle)*dx/2], 'k-')

                centre, = ax.plot(xx, yy, '+', markersize=10)
                centre.axes.set_xlim([0, dimx])
                centre.axes.set_ylim([dimy-1, 0])

                # Cross section
                crossx, = sideax.plot(xl, xcut)
                crossx.axes.set_ylim([254, 0])
                crossx.axes.set_xlim([0, 640])

                # stamp = str(int(time()))[4:]
                # outname = 'img_%s' %(stamp)
                # np.save(outname, data)
                # pl.savefig("%s.pdf" %outname)
                # pl.savefig("%s.png" %outname)
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
