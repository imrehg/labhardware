import numpy as np
import pylab as pl
import sys
sys.path.append('../../lablib')
import ourgui

def smoothList(list,strippedXs=False,degree=10):
    if strippedXs==True: return Xs[0:-(len(list)-(len(list)-degree+1))]
    smoothed=[0]*(len(list)-degree+1)
    for i in range(len(smoothed)):
        smoothed[i]=sum(list[i:i+degree])/float(degree)
    return smoothed

def smoothListGaussian(list,strippedXs=False,degree=5):
     window=degree*2-1
     weight=np.array([1.0]*window)
     weightGauss=[]
     for i in range(window):
         i=i-degree+1
         frac=i/float(window)
         gauss=1/(np.exp((4*(frac))**2))
         weightGauss.append(gauss)
     weight=np.array(weightGauss)*weight
     smoothed=[0.0]*(len(list)-window)
     for i in range(len(smoothed)):
         smoothed[i]=sum(np.array(list[i:i+window])*weight)/sum(weight)
     return smoothed

filename = ourgui.openFile()
dtypes = {'names': ['date', 'value', 'unit'],
          'formats': ['f8', 'f4', 'S1']}
data = np.loadtxt(filename,
                  delimiter=",",
                  dtype=dtypes,
                  )
date = data['date']
date -= date[0]
scale = 60
date /= scale
pl.plot(date, data['value'], '.')
degree = 200

sdataG = smoothListGaussian(data['value'], degree=degree)
sdateG = date[degree:(-degree+1)]

sdata = smoothList(data['value'], degree=degree)
sdate = date[degree/2:-degree/2+1]

pl.plot(sdate, sdata, 'g-')
pl.plot(sdateG, sdataG, 'r-')
pl.xlabel("time (min)")
pl.ylabel("thermistor resistance")
pl.show()
