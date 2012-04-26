"""
Trigger task with NI USB-6229 USB
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
DAQmx_Val_ContSamps = 10123
DAQmx_Val_GroupByChannel = 0
DAQmx_Val_ChanPerLine = 0
DAQmx_Val_ChanForAllLines = 1
DOUBLEPTR = ctypes.POINTER(ctypes.c_double)
clockSource = ctypes.create_string_buffer('PFI4')
# clockSource = ctypes.create_string_buffer('OnboardClock')
##############################
def CHK(err):
    """a simple error checking routine"""
    if err < 0:
        buf_size = 100
        buf = ctypes.create_string_buffer('\000' * buf_size)
        nidaq.DAQmxGetErrorString(err,ctypes.byref(buf),buf_size)
        raise RuntimeError('nidaq call failed with error %d: %s'%(err,repr(buf.value)))

#### Device
class NIDAQ():
    voltlimits = [10, 5, 2, 1, 0.5, 0.2, 0.1]

    def __init__(self, name="Dev1"):
        self.name = name

    def createTrigger(self, channel="PFI0", pulseLength=1, pulseSpacing=1, pulseRepeat=5, *args, **kwargs):
        return TriggerPulse(self, channel, pulseLength, pulseSpacing, pulseRepeat *args, **kwargs)

#### Task class
class TriggerPulse():
    # voltlimits = [10, 5, 2, 1, 0.5, 0.2, 0.1]

    def __init__(self, device, channel, pulseLength, pulseSpacing, pulseRepeat):
        """ Set up a voltage measurement task """
        self.taskHandle = TaskHandle(0)
        self.device = device
        # self.channelName = "%s/%s" %(device.name, channel)
        self.channelName = "Dev1/port0/line1,Dev1/port0/line0"
        CHK(nidaq.DAQmxCreateTask("PulseOut",ctypes.byref(self.taskHandle)))
        CHK(nidaq.DAQmxCreateDOChan(self.taskHandle,
                                    self.channelName,
                                    "",
                                    DAQmx_Val_ChanForAllLines,
                                    )
            )
        rate = 10
        # val = 2**30-1-1
        val = 1
        print("Value: %s" %bin(val))
        # pulses = numpy.array([val, 0, 0, 0, 0, val, val, val], dtype=numpy.uint32)
        # pulses = numpy.array([val, 0, val, 0, val, 0, val, 0], dtype=numpy.uint32)
        # external clock: 50kHz: 1 time unit is 20us
        sequence = [(0, 5, 3),  # pulse 1: 100us
                    (5, 50, 0), # delay: 1ms
                    (50, 55, 3), # pulse 2: 100us:
                    (55, 10000, 0), # long delay
                    ]
        pulses = numpy.zeros((500, 1), dtype=numpy.uint32)
        maxval = sequence[-1][1]
        pulses = numpy.zeros((maxval, 1), dtype=numpy.uint32)
        for i in range(maxval):
            for p in sequence:
                if p[0] <= i < p[1]:
                    pulses[i] = p[2]
            # if i % 2 == 0:
            #     pulses[i] = pulses[i] | 1

        CHK(nidaq.DAQmxCfgSampClkTiming(self.taskHandle,
                                        clockSource,
                                        float64(rate),
                                        DAQmx_Val_Rising,
                                        DAQmx_Val_ContSamps,
                                        uInt64(len(pulses))
                                        )
            )
        CHK(nidaq.DAQmxWriteDigitalU32(self.taskHandle,
                                       int32(len(pulses)),
                                       False,
                                       float64(5),
                                       DAQmx_Val_GroupByChannel,
                                       ctypes.cast(pulses.ctypes.data, DOUBLEPTR),
                                       None,
                                       None)
            )

    #     samples = DAQmx_Val_FiniteSamps if self.finite else DAQmx_Val_ContSamps
    #     CHK(nidaq.DAQmxCfgSampClkTiming(self.taskHandle,
    #                                     "",
    #                                     float64(rate),
    #                                     DAQmx_Val_Rising,
    #                                     samples,
    #                                     uInt64(self.maxsample)
    #                                     )
    #         )

    # def SetTrigger(self, triggerchannel="PFI0"):
    #     channel = triggerchannel
    #     CHK(nidaq.DAQmxCfgDigEdgeStartTrig(self.taskHandle,
    #                                        channel,
    #                                        DAQmx_Val_Rising
    #                                        )
    #         )

    def Start(self):
        """ Start the task """
        # Seems to take about 70ms to run this. Why?
        CHK(nidaq.DAQmxStartTask(self.taskHandle))

    def Stop(self):
        """ Stop the task """
        if self.taskHandle != 0:
            nidaq.DAQmxStopTask(self.taskHandle)

    # def Read(self, num=None):
    #     """ Read values """
    #     if num is None:
    #         num = self.maxsample
    #     read = int32()
    #     data = numpy.zeros((self.maxsample,), dtype=numpy.float64)
    #     CHK(nidaq.DAQmxReadAnalogF64(self.taskHandle,
    #                                  self.maxsample,
    #                                  float64(num),
    #                                  DAQmx_Val_GroupByChannel,
    #                                  data.ctypes.data,
    #                                  self.maxsample,
    #                                  ctypes.byref(read),
    #                                  None)
    #         )
    #     return (read, data)

    def Close(self):
        """ Close the task """
        if self.taskHandle != 0:
            self.Stop()
            nidaq.DAQmxClearTask(self.taskHandle)

    def Wait(self):
        """ Wait until task is done """
        CHK(nidaq.DAQmxWaitUntilTaskDone(self.taskHandle, float64(120)))

 
if __name__ == "__main__":
    dev = NIDAQ()
    task0 = dev.createTrigger(channel="port0/line0")
    task0.Start()
    raw_input("Enter to stop")
    task0.Close()
    
    # import pylab as pl
    # import time
    # dev = NIDAQ()
    # sample = 10000
    # rate = sample
    # task0 = dev.createTask(channel="ai1", maxsample=sample, rate=rate, voltlimit=0.5)

    # task0.Start()
    # read, data = task0.Read()
    # task0.Stop()

    # totaltime = sample / rate
    # times = numpy.linspace(0, totaltime, sample)
    # task0.Close()
    # pl.plot(times, data)
    # pl.xlabel("Time (s)")
    # pl.ylabel("Recorded signal (V)")
    # pl.show()
