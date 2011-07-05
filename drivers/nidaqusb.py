"""
Driver module for NI USB-6259 DAQ
"""
from __future__ import division
import ctypes
import numpy
nidaq = ctypes.windll.nicaiu # load the DLL

##############################
# Setup some typedefs and constants
# to correspond with values in
# C:\Program Files\National Instruments\NI-DAQ\DAQmx ANSI C Dev\include\NIDAQmx.h
# the typedefs
int32 = ctypes.c_long
uInt32 = ctypes.c_ulong
uInt64 = ctypes.c_ulonglong
float64 = ctypes.c_double
TaskHandle = uInt32
# the constants
DAQmx_Val_Cfg_Default = int32(-1)
DAQmx_Val_Volts = 10348
DAQmx_Val_Rising = 10280
DAQmx_Val_FiniteSamps = 10178
DAQmx_Val_GroupByChannel = 0
##############################
def CHK(err):
    """a simple error checking routine"""
    if err < 0:
        buf_size = 100
        buf = ctypes.create_string_buffer('\000' * buf_size)
        nidaq.DAQmxGetErrorString(err,ctypes.byref(buf),buf_size)
        raise RuntimeError('nidaq call failed with error %d: %s'%(err,repr(buf.value)))

#### Device class
class NIDAQ():
    voltlimits = [10, 5, 2, 1, 0.5, 0.2, 0.1]

    def __init__(self, name="Dev1"):
        self.name = name

    def createTask(self, channel="ai0", maxsample=1000, rate=1000, voltlimit=10.0):
        return Task(self, channel, maxsample, rate, voltlimit)

#### Task class
class Task():
    # voltlimits = [10, 5, 2, 1, 0.5, 0.2, 0.1]

    def __init__(self, device, channel="ai0", maxsample=1000, rate=1000, voltlimit=10.0):
        """ Set up a voltage measurement task """
        self.taskHandle = TaskHandle(0)
        self.channelName = "%s/%s" %(device.name, channel)
        self.maxsample = maxsample
        CHK(nidaq.DAQmxCreateTask("",ctypes.byref(self.taskHandle)))
        CHK(nidaq.DAQmxCreateAIVoltageChan(self.taskHandle,
                                           self.channelName,
                                           "",
                                           DAQmx_Val_Cfg_Default,
                                           float64(-voltlimit),
                                           float64(voltlimit),
                                           DAQmx_Val_Volts,
                                           None
                                           )
            )
        CHK(nidaq.DAQmxCfgSampClkTiming(self.taskHandle,
                                        "",
                                        float64(rate),
                                        DAQmx_Val_Rising,
                                        DAQmx_Val_FiniteSamps,
                                        uInt64(self.maxsample)
                                        )
            )

    def Start(self):
        """ Start the task """
        # Seems to take about 70ms to run this. Why?
        CHK(nidaq.DAQmxStartTask(self.taskHandle))

    def Stop(self):
        """ Stop the task """
        if self.taskHandle != 0:
            nidaq.DAQmxStopTask(self.taskHandle)

    def Read(self, num=None):
        """ Read values """
        if num is None:
            num = self.maxsample
        read = int32()
        data = numpy.zeros((self.maxsample,), dtype=numpy.float64)
        CHK(nidaq.DAQmxReadAnalogF64(self.taskHandle,
                                     self.maxsample,
                                     float64(num),
                                     DAQmx_Val_GroupByChannel,
                                     data.ctypes.data,
                                     self.maxsample,
                                     ctypes.byref(read),
                                     None)
            )
        return (read, data)

    def Close(self):
        """ Close the task """
        if self.taskHandle != 0:
            self.Stop()
            nidaq.DAQmxClearTask(self.taskHandle)

if __name__ == "__main__":
    """
    Example code to try this class: record 1s worth of 1000 voltage datapoints on AI0
    """
    import pylab as pl
    import time
    dev = NIDAQ()
    sample = 10000
    rate = sample
    task0 = dev.createTask(channel="ai1", maxsample=sample, rate=rate, voltlimit=0.5)

    task0.Start()
    read, data = task0.Read()
    task0.Stop()

    totaltime = sample / rate
    times = numpy.linspace(0, totaltime, sample)
    task0.Close()
    pl.plot(times, data)
    pl.xlabel("Time (s)")
    pl.ylabel("Recorded signal (V)")
    pl.show()
