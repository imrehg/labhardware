from __future__ import division

from time import sleep
from numpy import *
import agilent8644
import stanfordSR830

synth = agilent8644.Agilent8644(7)
lockin = stanfordSR830.StanfordSR830(8)

clock =  9192631770
clockscan = [-5, 5]

synthmulti = 20

scansteps = 5
repeats = 5

synth.write("FREQ:CW %f HZ" %(clock/synthmulti))

q = ["FREQ:CW?"]
for quest in q:
    print quest, "->", synth.ask(quest)

lockin.write("REST")
lockin.write("SRAT 8")
lockin.write("FAST 0")
q = ["SRAT?", "SPTS?", "SEND?"]
for quest in q:
    print quest, "->", lockin.ask(quest)

print ">>>>>>>>>>>>>>>>>>>>>>>>>>>"

ss = linspace(clockscan[0],clockscan[1],scansteps)
results = zeros((scansteps, 2))
for index, scanning in enumerate(ss):
    freq = clock + scanning
    print "Detuning %d / %d: %f Hz" %(index+1, scansteps, scanning) 
    synth.write("FREQ:CW %f HZ" %(freq/synthmulti))
    # Let it settle
    sleep(1)
    lockin.write("REST")
    lockin.write("STRT")
    # Wait until there's enough data
    while (int(lockin.ask("SPTS?")) < repeats):
        sleep(0.5)
    lockin.write("PAUS")
    temp = lockin.ask("TRCA?1,0,%d" %(repeats))
    temp2 = array([float(x) for x in temp.split(',')[0:-1]])
    results[index, 0:2] = [freq, average(temp2)]

savetxt('test.out',results)
