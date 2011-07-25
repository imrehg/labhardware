import serial

class GPS:

    def __init__(self, com):
        self.__ser = serial.Serial('/dev/ttyUSB0',
                                   baudrate=9600,
                                   bytesize=8, stopbits=1,
                                   parity=serial.PARITY_NONE,
                                   timeout=1,
                                   )


    def checksum(self, msg):
        chk = ord(msg[0]) ^ ord(msg[1])
        for i in xrange(2, len(msg)):
            chk = chk ^ ord(msg[i])
        return chr(chk)

    def ask(self, query):
        message = "@@%s%s\r\n" %(query, self.checksum(query))
        print "Query: %s, (%d)" %(query, len(message))
        self.__ser.write(message)
        response = self.__ser.readline()
        while response[-2:] != '\r\n':
            response += self.__ser.readline()
        return response

if __name__ == "__main__":
    gps = GPS(0)
    # line = gps.ask("Hn0")
    line = gps.ask("Bb0")
    resp = line[2:4]
    print len(line)
    if resp == "Bb":
        numsat = ord(line[4])
        s = 5
        for i in xrange(numsat):
            print ord(line[s])
            s += 7
