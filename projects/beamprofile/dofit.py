from __future__ import division
import pydc1394 as fw
from time import sleep, time
import numpy as np
import pylab as pl
import matplotlib.cm as cm

import gaussfitter as gf

if __name__ == "__main__":
    filename = 'img_343444'
    # filename = 'img'
    data = np.load('%s.npy' %filename)

    fit = gf.gaussfit(data)
    cmap = cm.gist_gray
    cmap = cm.jet

    fig = pl.figure(num=1, figsize=(11.69, 8.27))
    pl.subplot(221)
    pl.imshow(data, cmap=cmap)
    pl.title('Image')
    pl.xlabel('x')
    pl.ylabel('y')

    pl.subplot(224)
    fdata = np.ravel((gf.twodgaussian(fit,0,1,1)\
                (*np.indices(data.shape)))).reshape(np.shape(data))
    pl.imshow(fdata)
    pl.xlabel('Fitted data')

    xc = fit[2]
    yc = fit[3]
    xcr, ycr = np.round(xc), np.round(yc)

    # Cross sections
    pl.subplot(223)
    xp, = pl.plot(range(640), data[ycr, :], 'k-')
    xp2, = pl.plot(range(640), fdata[ycr, :], 'b-', linewidth=2)
    pl.xlabel('x cross section at y=%d' %(ycr))
    pl.xlim([0, 640])
    pl.ylim([0, 255])
    xp.axes.set_ylim(xp.axes.get_ylim()[::-1])

    pl.subplot(222)
    yp, = pl.plot(data[:, xcr], range(480), 'k-')
    yp2, = pl.plot(fdata[:, xcr], range(480), 'b-', linewidth=2)
    pl.xlabel('y cross section at x=%d' %xcr)
    pl.xlim([0, 255])
    pl.ylim([0, 480])
    yp.axes.set_ylim(yp.axes.get_ylim()[::-1])

    pixel = 5.6e-3 # (5.6um in mm)
    sx = fit[4]*2
    sy = fit[5]*2
    rot = fit[6]

    info = "Center position: (%.1f, %.1f)px ; 1/e^2 widths (%.1f, %.1f)px / (%.3f, %.3f) mm; rotation (%.1f) deg" %(xc, yc, sx, sy, sx*pixel, sy*pixel, rot)
    fig.text(0.5, 0.95, info, horizontalalignment='center')

    pl.savefig('%s.pdf' %filename)
    pl.savefig('%s.png' %filename)
    pl.show()
