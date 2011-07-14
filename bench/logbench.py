"""
Benchmarking save to the harddrive to see what to use next time in high speed
logging code.
"""
import numpy
import random
import sys
import time

# Own import
sys.path.append("../")
import lablib.logfile

def logiter(digits, maxval):
    """ 
    Logarithmic iterator
    
    digits: the leading digits to use
    maxval: maximum value to return (inclusive)
    E.g. digits = [1, 3], maxval = 100 will yield 1,3,10,30,100.
    """
    i, power = 0, 0
    val = digits[i]
    while val <= maxval:
        yield val
        i += 1
        if i >= len(digits):
            i, power = 0, power + 1
        val = digits[i] * 10**power

# Start logfile
log = lablib.logfile.setupLog()

maxval = 10000
niter = logiter([1, 2, 5], maxval)
data = numpy.random.rand(maxval)

#### Logger module save
print "Logger module:\n"+"="*20
for n in niter:
    start = time.time()
    for v in data[0:n]:
        log(v)
    elapsed = time.time()-start
    print("%6d -> lapsed: %f s, %f data/s" %(n, elapsed, n/elapsed))

print("")

#### Numpy save
filename = "numpy_%d.log" %(numpy.random.rand(1)*1000)  # just a unique filename
niter = logiter([1, 2, 5], maxval)
print "Numpy module (%s):\n" %(filename)+"="*20
for n in niter:
    start = time.time()
    f = open(filename, "w") # In the normal situation this would be append
    numpy.savetxt(f, data[0:n], delimiter=",")
    f.close()
    elapsed = time.time()-start
    print("%6d -> lapsed: %f s, %f data/s" %(n, elapsed, n/elapsed))

### On lab-desktop: 15ks/s <-> 170ks/s in favor of numpy (when one column, 4 colum: 66ks/s)
