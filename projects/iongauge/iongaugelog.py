#!/usr/bin/env python

# RS-232 Serial support for Varian XGS-600 ion gauge

import serial
import re
from time import time, sleep
import logging
logger = logging.getLogger('serialmulti')
hdlr = logging.FileHandler('./gauge.log')
formatter = logging.Formatter('%(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)

class IonGauge:

    def __init__(self, port='/dev/ttyUSB0', baudrate=9600):
        import serial
        self.serialconn = serial.Serial(port, baudrate, bytesize=8, \
            stopbits=1, parity=serial.PARITY_NONE, timeout=1, xonxoff=0, \
            rtscts=0, dsrdtr=0)
        print("System operational.")

    def close(self):
        self.serialconn.close()
	
    def query(self, command):
        self.serialconn.write("%s\r" %(command))
        response = self.serialconn.readline().strip()
        return(response[1:])

MOT1 = IonGauge()
try:
    while True:
        pressure = MOT1.query("#0002UMOT1")
        logger.info("%f %s" % (time(), pressure))
        print("Pressure: %s torr" %(pressure))
	sleep(2)
except (KeyboardInterrupt):
    # Exit with Control-C
    pass
except:
    raise
finally:
    MOT1.close()
