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
        self.write(query)
        response = self.__ser.readline()
        while response[-2:] != '\r\n':
            response += self.__ser.readline()
        return response

    def write(self, message):
        message = "@@%s%s\r\n" %(message, self.checksum(message))
        print "Message: %s" %message
        self.__ser.write(message)

    def parse(self, resp):
        if len(resp) < 4:
            return
        rtype = resp[2:4]
        if rtype == "Bb":
            out = {'code': rtype,
                   'info': "Visible satellite data message",
                   }
            out['nsat'] = ord(line[4])
            sat, s = [], 5
            for i in xrange(out['nsat']):
                sat += [{'id': ord(resp[s]),
                          'elevation': ord(resp[s+3]),
                          'azimuth': ord(resp[s+4])*256 + ord(resp[s+5])}]
                s += 7
            out['sats'] = sat
            return out
        elif rtype == 'Ge':
            out = {'code': rtype,
                   'info': 'Time-RAIM select message'}
            out['status'] = True if ord(resp[4]) == 1 else False
            return out
        elif rtype == 'Ha':
            out = {'code': rtype,
                   'info': '12 channel position/status/data message',
                   }
            date = {'month': ord(resp[4]),
                    'day': ord(resp[5]),
                    'year': ord(resp[6])*256 + ord(resp[7]),
                    }
            out['date'] = date
            time = {'hour': ord(resp[8]),
                    'minute': ord(resp[9]),
                    'second': ord(resp[10]),
                    'nanosecond': ord(resp[11])*256**3 + ord(resp[12])*256**2 + ord(resp[13])*256 + ord(resp[14]),
                    }
            out['time'] = time
            lat = (ord(resp[15])*256**3 + ord(resp[16])*256**2 + ord(resp[17])*256 + ord(resp[18]))/324e6*90
            lon = (ord(resp[19])*256**3 + ord(resp[20])*256**2 + ord(resp[21])*256 + ord(resp[22]))/648e6*180
            position = {'latitude': lat,
                        'longitude': lon,
                        'pos': "%f,%f" %(lat, lon)
                        }
            out['position'] = position
            return out
        elif rtype == 'AP':
            out = {'code': rtype,
                   'info': 'Pulse mode select command'}
            out['status'] = '100PPS' if ord(resp[4]) == 1 else '1PPS'
            return out
        elif rtype == 'Gd':
            out = {'code': rtype,
                   'info': 'Position control message'}
            scode = ord(resp[4])
            if scode == 0:
                status = 'enable normal 3D positioning'
            elif scode == 1:
                status = 'enable position hold'
            elif scode == 2:
                status = 'enable 2D positioning'
            elif scode == 3:
                status = 'enable auto-survey'
            else:
                status = 'unknown'
            out['status'] = status
            return out


if __name__ == "__main__":
    gps = GPS(0)
    # line = gps.ask("Hn0")
    line = gps.ask("Bb"+chr(0))
    resp = gps.parse(line)
    if resp:
        if resp['code'] == 'Bb':
            print "%s: (%d)" %(resp['info'], resp['nsat'])
            for sat in resp['sats']:
                print "ID: %d, pos: %d / %d" %(sat['id'], sat['elevation'], sat['azimuth'])

    tr = gps.ask("Ha"+chr(0))
    print gps.parse(tr)

    # print gps.ask("AM"+chr(255)+chr(255)+chr(255)+chr(255))
    # gps.write("AP"+chr(0))
    # print gps.parse(gps.ask("AP"+chr(255)))

    # gps.write("Gd"+chr(3))
    print gps.parse(gps.ask("Gd"+chr(255)))

    print gps.parse(gps.ask("Ge"+chr(255)))
