from __future__ import division
import numpy as np
import pylab as pl
from mpl_toolkits.axes_grid1 import make_axes_locatable

import fastfit

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
    ctext = "wx : wy\n%.1f %s %.1f" %(sx, csign, sy)
    return ctext

def limits(centre, out, valid):
    """ Calculate matrix borders with limits """
    bottom = max(valid[0], centre-out)
    top = min(valid[1], centre+out)
    return bottom, top

def gauss(x, x0, sx, scale):
    """ Simple gaussian """
    return np.exp(-(x-x0)**2 / (2 * sx**2)) * scale

def preparedata(data):
    """ Prepare data for processing by cutting down on the area for D4s

    Input:
    ------
    data: original reading values in numpy array from

    Output:
    ------
    prepared: data in the cropped area
    (xbottom, ybottom): value of the starting corner in two dimension
    """
    dh, dw = data.shape
    border = np.array([])
    border = np.append(border, np.ravel(data[:-1, 0]))
    border = np.append(border, np.ravel(data[0, 1:]))
    border = np.append(border, np.ravel(data[1:, -1]))
    border = np.append(border, np.ravel(data[-1, :-1]))
    borderavg, bordervar = np.mean(border), np.var(border)
    slimdata = np.copy(data) - borderavg
    maxy, maxx = np.unravel_index(np.argmax(slimdata), slimdata.shape)
    # Find the number of points in the x/y direction that are above the background noise
    xl = slimdata[:, maxx]
    xdim = sum(sum([xl > 10*bordervar]))
    yl = slimdata[maxy, :]
    ydim = sum(sum([yl > 10*bordervar]))
    dim = 2 * max(xdim, ydim)
    if dim < 5:
        # In this case, most likely we don't have a peak, just noise, since
        # very few points are over the noiselevel
        return data, (0, 0)
    xbottom, xtop = limits(maxx, dim, (0, dw))
    ybottom, ytop = limits(maxy, dim, (0, dh))
    testdata = slimdata[ybottom:ytop, xbottom:xtop]
    xx, yy, dx, dy, angle = fastfit.d4s(testdata)

    xc = int(xbottom+xx)
    yc = int(ybottom+yy)
    limr = 0.69
    limx = int(dx * limr)
    limy = int(dy * limr)
    xbottom, xtop = limits(xc, limx, (0, dw))
    ybottom, ytop = limits(yc, limy, (0, dh))
    prepared = slimdata[ybottom:ytop, xbottom:xtop]
    return prepared, (xbottom, ybottom)

def analyze(data):
    """ Do all the analysis that's needed to create the interface """
    prepared, centre = preparedata(data)
    xx, yy, dx, dy, angle = fastfit.d4s(prepared)
    xx += centre[0]
    yy += centre[1]
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
    sy, sx = data.shape
    xcut = data[yc, :]
    ycut = data[:, xc]
    xline = range(0, sx)
    yline = range(0, sy)
    xcutg = gauss(xline, xx, xwidth, max(xcut))
    ycutg = gauss(yline, yy, ywidth, max(ycut))
    return (xx, yy, dx, dy, angle, xr, yr, adeg, xxx, xxy, yyx, yyy, xwidth, ywidth, xc, yc, xcut, ycut, xcutg, ycutg)

def createiface(data):
    (xx, yy, dx, dy, angle, xr, yr, adeg, xxx, xxy, yyx, yyy, xwidth, ywidth, xc, yc, xcut, ycut, xcutg, ycutg) = analyze(data)
    sy, sx = data.shape

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
    fitlinewidth=2
    axCuty = divider.append_axes("right", size=1.4, pad=0.1, sharey=axImg)
    yl, = axCuty.plot(ycut, yline, 'k-', linewidth=cutlinewidth)
    yg, = axCuty.plot(ycutg, yline, 'r-', linewidth=fitlinewidth)

    axCutx = divider.append_axes("bottom", size=1.4, pad=0.1, sharex=axImg)
    xl, = axCutx.plot(xline, xcut, 'k-', linewidth=cutlinewidth)
    xg, = axCutx.plot(xline, xcutg, 'r-', linewidth=fitlinewidth)

    # Setting up limits
    axImg.set_xlim([0, sx])
    axImg.set_ylim([sy, 0])
    axImg.set_xticks([])
    axImg.set_yticks([])

    axCuty.set_xlim([-10, 256])
    axCuty.set_xticks([0, 128, 256])

    axCutx.set_ylim([256, -10])
    axCutx.set_yticks([0, 128, 256])

    # Header text
    htext = fig.text(0.5,
                     0.99,
                     'wx,wy = D4s/2*pixelsize [um] along principal axes\n = beam waists for Gaussian beam',
                     horizontalalignment='center',
                     verticalalignment='top',
                     fontsize=16,
                     family='monospace',
                     )
    # Size text
    sztext = fig.text(0.5,
                      0.81,
                      st,
                      horizontalalignment='center',
                      verticalalignment='baseline',
                      fontsize=67,
                      family='monospace',
                      )
    # Angle text
    atext = fig.text(0.5,
                     0.10,
                     adeg,
                     horizontalalignment='center',
                     verticalalignment='baseline',
                     fontsize=65,
                     family='monospace')
    # Rangetext
    uptext = fig.text(0.5,
                      0.05,
                      text,
                      horizontalalignment='center',
                      verticalalignment='baseline',
                      fontsize=25,
                      family='monospace',
                      )

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
