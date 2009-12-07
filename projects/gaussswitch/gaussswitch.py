# Switching the magnetic field coils and recording the magnetic field change

from nidaqmx import AnalogInputTask, DigitalOutputTask
from time import sleep, strftime
from numpy import savetxt, linspace, column_stack

####################################
## Settings

# Analog Input rate (1/s)
airate = 300000

# Recorded points
numpoints = 30000

####################################


class Relay:

    def __init__(self, channel, value=0):
        ''' Simple relay class

        Input params:
        channel : name of digital channel. E.g. "Dev2/port1/line0"
        value=0 : starting value of the output.
        '''
        self._relay = DigitalOutputTask()
        self._relay.create_channel(channel)
        self.set(value)

    def set(self, value):
        ''' Set the output of the digital channel

        Input params:
        value : set output to this [0, 1]
        '''
        if value in [0, 1]:
            self.value = value
            self._relay.write(self.value,auto_start=True,timeout=1)
        else:
            raise(ValueError)

    def toggle(self):
        ''' Toggle the relay between the two possible valies'''
        self.set(1-self.value)

class Sensors:

    def __init__(self, channels, minv=-10.0, maxv=10.0, srate=1000, snum=1000):
        self._sensor = AnalogInputTask()
        self._sensor.create_voltage_channel(channels, min_val=minv,
            max_val=maxv)
        self._sensor.configure_timing_sample_clock(rate=srate,
            sample_mode='finite', samples_per_channel=snum)

    def start(self):
        self._sensor.start()

    def stop(self):
        self._sensor.stop()

    def wait_until_done(self, timeout = 10):
        self._sensor.wait_until_done(timeout)

    def read(self):
        return self._sensor.read()


# Setup hardware
relay = Relay("Dev2/port1/line0", value = 0)
mag = Sensors("Dev2/ai0:2", minv = -5.0, maxv = 5.0,
    srate = airate, snum = numpoints)

# Method:
# 1) Turn on magnetic field, wait until settles.
# 2) Start recording
# 3) Turn off relay
# 4) Read data

relay.set(value = 1)
sleep(2)

mag.start()
sleep(0.01)
relay.toggle()
mag.wait_until_done(timeout=2)
aidata = mag.read()

tstep = 1.0/airate
tottime = (numpoints - 1) * tstep
timedata = linspace(0, tottime, numpoints)

# Setting up output file
datafile = "gauss_%s.log" %(strftime("%y%m%d_%H%M%S"))
out = file(datafile, 'a')
out.write("#Time(s) Voltage(V):Ch1 / Ch2 / Ch3\n")
savetxt(out, column_stack((timedata, aidata)))
out.close()

del mag
del relay

print "Finished: %s" %(datafile)