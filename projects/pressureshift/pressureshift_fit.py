from numpy import *
from pylab import *
from ourgui import openFile
from scipy.optimize import leastsq
import scipy.odr
from scipy.special import wofz
filename = openFile(type='log')
#filename = 'pressureshift_100601_160335.log'
#filename = 'pressureshift_100601_160839.log'
#filename = 'pressureshift_100601_163015.log'

f, r, th = loadtxt(filename, comments='#', delimiter=',', unpack=True)

# Check how many repetitions are there
n = 0
for res in f:
    if res == f[0]:
        n += 1
    else:
        break

points = len(f) / n;
repeats = n

avgs = []
errbar = []
favgs = []
for i in xrange(0, points):
    try:
        avgs.append(average(r[i*repeats:(i+1)*repeats]))
        errbar.append(std(r[i*repeats:(i+1)*repeats]))
        favgs.append(f[i*repeats])
    except:
        break
mm = argmax(avgs)
fm = favgs[mm]

# lim = 600000
# fitx = f[abs(f-fm) <= lim]
# fity = r[abs(f-fm) <= lim ]
# fity = fity / max(fity)
fitx = f
fity = r/max(r)

fitfunc = lambda p, x: p[2]*exp(-(x-p[0])**2 / (2*p[1]**2)) + p[3]
errfunc = lambda p, x, y: fitfunc(p, x) - y
xx = linspace(min(fitx), max(fitx), 200)
p0 = [100000, 50000, 1, 0.1]


# p1, success = leastsq(errfunc, p0, args=(fitx, fity))

# print "Centre: %f kHz" %(p1[0]/1e3)
# print "Width : %f kHz" %(p1[1]/1e3)
# print "Scale : %f" %(p1[2])
# print "Offset: %f" %(p1[3])
# plot(fitx, fity, '.')
# plot(xx, fitfunc(p1,xx),'-')
# show()

p0 = [100000, 50000, 100000, 0.1, 2000]
fitfunc = lambda p, x: p[2]*real(wofz(((x-p[0])+i*p[4])/(p[1]*sqrt(2))))/(p[1]*sqrt(2*pi)) + p[3]

data = scipy.odr.Data(fitx, fity)
model = scipy.odr.Model(fitfunc)
fit = scipy.odr.ODR(data, model, p0, maxit=200000)
fit.set_job(fit_type=2)
output = fit.run()
output.pprint()
plot(fitx, fity, '.')
plot(xx, fitfunc(output.beta,xx),'-')
show()
