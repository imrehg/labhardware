import numpy as np
import pylab as pl
import sys

filename = sys.argv[1]
dtypes = {'names': ('date', 'value', 'unit'),
          'formats': ('f8', 'f4', 'S1')}
data = np.loadtxt(filename,
                  delimiter=",",
                  dtype=dtypes,
                  unpack=True)

date = data['date']
date -= date[0]
scale = 60
date /= scale
pl.plot(date, data['value'], '.')
pl.xlabel("time (min)")
# pl.xlabel("time (h)")
pl.ylabel("thermistor resistance")
pl.show()
