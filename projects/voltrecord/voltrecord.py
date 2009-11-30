#Acq_IncClk.py
# C:\Program Files\National Instruments\NI-DAQ\Examples\DAQmx ANSI C\Analog In\Measure Voltage\Acq-Int Clk\Acq-IntClk.c
import ctypes
import numpy
from time import time, strftime
nidaq = ctypes.windll.nicaiu # load the DLL

#########################
### Setting parameters

# Voltage limit: record between -voltlimit...+voltlimit
voltlimit = 2.0


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
# initialize variables
taskHandle = TaskHandle(0)

class AIChannel:
    def __init__(self, nidaq, device, channel, voltlimit, max_num_samples):
        self.taskHandle = TaskHandle(0)
        self.nidaq = nidaq
        self.max_num_samples = max_num_samples
        self.voltlimit = voltlimit
        self.data = numpy.zeros((self.max_num_samples,),dtype=numpy.float64)
        # now, on with the program
        CHK(self.nidaq.DAQmxCreateTask("",ctypes.byref(self.taskHandle)))
        CHK(self.nidaq.DAQmxCreateAIVoltageChan(self.taskHandle,"Dev2/ai0","",
                                   DAQmx_Val_Cfg_Default,
                                   float64(-self.voltlimit),float64(self.voltlimit),
                                   DAQmx_Val_Volts,None))
    def startTask(self):
        CHK(self.nidaq.DAQmxStartTask(self.taskHandle)) 
        self.read = int32()

    def readValue(self):
        CHK(self.nidaq.DAQmxReadAnalogF64(self.taskHandle,self.max_num_samples,float64(10.0),
                             DAQmx_Val_GroupByChannel,self.data.ctypes.data,
                             self.max_num_samples,ctypes.byref(self.read),None))
        return self.data


# Setting up input
chan = AIChannel(nidaq, "Dev2", "ai0", voltlimit, 1)
chan.startTask()

# Setting up output file
datafile = "errorsig_%s.log" %(strftime("%y%m%d_%H%M%S"))
out = file(datafile, 'a')
out.write("#Time(UnixTime) Voltage(V)\n")

# Do logging until stopped by Ctrl-C
while True:
    try:
        now = time()
        errorsignal = chan.readValue()
        result = numpy.array([[now, errorsignal]])
        numpy.savetxt(out, result)
        print "%f / %f V " %(now, errorsignal)
    except (KeyboardInterrupt):
        break
out.close()
    
    