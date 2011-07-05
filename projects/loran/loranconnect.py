import loran


timebase = loran.FS700(17)

# timebase.startacq(74300)

queries = ["GAIN?", "FLLT?", "GRIP?", "STTN?", "LSTA?", "NSTA?", "STON?", "TLCK?", "TULK?"]
for q in queries:
    print "%s -> %s " %(q, timebase.ask(q))

nstas = int(timebase.ask("NSTA?"))
for i in xrange(0, nstas):
    print "Station %d: %s" %(i, timebase.ask("INFO? %d" %i))
