"""
2D Gaussian fitting, based on http://www.scipy.org/Cookbook/FittingData#head-11870c917b101bb0d4b34900a0da1b7deb613bf7
"""
import numpy as np
import pylab as pl
from scipy import optimize

import fastfit

def gaussian(height, center_x, center_y, width_x, width_y, angle, offset):
    """Returns a gaussian function with the given parameters"""
    width_x = float(width_x)
    width_y = float(width_y)
    return lambda x,y: height * np.exp(
        -(((np.cos(angle)*(center_x-x) - np.sin(angle)*(center_y-y))/width_x)**2+
          ((np.sin(angle)*(center_x-x) + np.cos(angle)*(center_y-y))/width_y)**2)/2)+offset

def fitgaussian(data):
    """Returns (height, x, y, width_x, width_y)
    the gaussian parameters of a 2D distribution found by a fit"""
    xx, yy, dx, dy, angle = fastfit.d4s(data)
    # For some reason x and y are exchanged
    params = [np.max(data), yy, xx, dy/4, dx/4, -angle, np.min(data)]
    errorfunction = lambda p: np.ravel(gaussian(*p)(*np.indices(data.shape)) -
                                 data)
    try:
        p, success = optimize.leastsq(errorfunction, params, maxfev=90)
    except:  # This should be triggered normally by KeyboardInterrupt but optimize throws different error that's hard to catch
        p = None  # to propagate stop signal upstream
    return p
