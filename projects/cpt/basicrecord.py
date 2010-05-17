import agilent8644
import stanfordSR830


synth = agilent8644.Agilent8644(7)
#lockin = stanfordSR830.StanfordSR830(8)


#synth.write("FREQ:CENT 91.6MHZ")
#synth.write("FREQ:SPAN 200Hz")
#synth.write("FREQ:SPAN:STEP:INC 10Hz")
synth.write("INIT:MODE SINGLE")
# synth.write("FREQ:MODE SWEEP")
# synth.write("INIT:IMM")


