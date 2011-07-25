import serial

def deepprint(dd, l=0):
    for k in dd:
        if type(dd[k]) == type({}):
            print "\t"*l, k
            deepprint(dd[k],l+1)
        elif type(dd[k]) == type([[]]):
            print "\t"*l, k, ": ", ", ".join([label[0] for label in dd[k]])
        else:
            print "\t"*l, k, ": ", dd[k]

def satstatus(stat):
    msg = []
    if (stat & 0b0001000000000000): msg += [['Narrow-band search mode']]
    if (stat & 0b0000100000000000): msg += [['Channel used for time solution']]
    if (stat & 0b0000010000000000): msg += [['Differential corrections available']]
    if (stat & 0b0000001000000000): msg += [['Invalid data']]
    if (stat & 0b0000000100000000): msg += [['Parity error']]
    if (stat & 0b0000000010000000): msg += [['Channel used for position fix']]
    if (stat & 0b0000000001000000): msg += [['Satellite momentum alert flag']]
    if (stat & 0b0000000000100000): msg += [['Satellite anti-spoof flag set']]
    if (stat & 0b0000000000010000): msg += [['Satellite reported unhealthy']]
    # Accuracy (Bits 3-0) not decoded yet
    return msg

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
            height = (ord(resp[23])*256**3 + ord(resp[24])*256**2 + ord(resp[25])*256 + ord(resp[26]))/100
            msl = ord(resp[27])*256**3 + ord(resp[28])*256**2 + ord(resp[29])*256 + ord(resp[30])
            position = {'latitude': lat,
                        'longitude': lon,
                        'pos': "%f,%f" %(lat, lon),
                        'height': height,
                        'msl': msl,
                        }
            out['position'] = position
            lat2 = (ord(resp[31])*256**3 + ord(resp[32])*256**2 + ord(resp[33])*256 + ord(resp[34]))/324e6*90
            lon2 = (ord(resp[35])*256**3 + ord(resp[36])*256**2 + ord(resp[37])*256 + ord(resp[38]))/648e6*180
            height2 = (ord(resp[39])*256**3 + ord(resp[40])*256**2 + ord(resp[41])*256 + ord(resp[42]))/100
            msl2 = ord(resp[43])*256**3 + ord(resp[44])*256**2 + ord(resp[45])*256 + ord(resp[46])
            position2 = {'latitude': lat2,
                        'longitude': lon2,
                        'pos': "%f,%f" %(lat2, lon2),
                        'height': height2,
                        'msl': msl2,
                        }
            out['position2'] = position2
            speed = {'3D': (ord(resp[47])*256 + ord(resp[48]))/100,
                     '2D': (ord(resp[49])*256 + ord(resp[50]))/100,
                     'heading': (ord(resp[51])*256 + ord(resp[52]))/10,
                     }
            out['speed'] = speed
            out['geometry'] = (ord(resp[53])*256 + ord(resp[54]))/10
            out['nsat'] = ord(resp[55])
            out['tsat'] = ord(resp[56])
            sats, ss = {}, 57
            ###
            modes = {0: 'Code search',
                     1: 'Code acquire',
                     2: 'AGC set',
                     3: 'Frequency acquire',
                     4: 'Bit sync detect',
                     5: 'Message sync detect',
                     6: 'Satellite time available',
                     7: 'Ephemeris acquire',
                     8: 'Available for position',
                     }
            ###
            for i in xrange(12):
                sat = {'SVID': ord(resp[ss]),
                       'mode': modes[ord(resp[ss+1])],
                       'signal strength': ord(resp[ss+2]),
                       'IODE': ord(resp[ss+3]),
                       }
                status = ord(resp[ss+4])*256 + ord(resp[ss+5])
                sat['status'] = satstatus(status)
                sats[i] = sat
                ss += 6
            out['satellites'] = sats
            fixstatus = ord(resp[ss])*256 + ord(resp[ss+1])
            fix = (fixstatus & 0b1110000000000000) >> 13
            fstats = {0b111: '3D fix',
                      0b110: '2D fix',
                      0b101:'Propagate mode',
                      0b100: 'Position hold',
                      0b011: 'Acquiring satellites',
                      0b010: 'Bad geometry',
                      0b001: 'Reserved',
                      0b000: 'Reserved',
                      }
            out['fixstatus'] = fstats[fix]
            return out
        elif rtype == 'Hb':
            out = {'code': rtype,
                   'info': 'Short position message',
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
            height = (ord(resp[23])*256**3 + ord(resp[24])*256**2 + ord(resp[25])*256 + ord(resp[26]))/100
            msl = ord(resp[27])*256**3 + ord(resp[28])*256**2 + ord(resp[29])*256 + ord(resp[30])
            position = {'latitude': lat,
                        'longitude': lon,
                        'pos': "%f,%f" %(lat, lon),
                        'height': height,
                        'msl': msl,
                        }
            out['position'] = position
            speed = {'3D': (ord(resp[31])*256 + ord(resp[32]))/100,
                     '2D': (ord(resp[33])*256 + ord(resp[34]))/100,
                     'heading': (ord(resp[35])*256 + ord(resp[36]))/10,
                     }
            out['speed'] = speed
            out['geometry'] = (ord(resp[37])*256 + ord(resp[38]))/10
            out['nsat'] = ord(resp[39])
            out['tsat'] = ord(resp[40])
            status = ord(resp[41])*256 + ord(resp[42])
            fix = (status & 0b1110000000000000) >> 13
            fstats = {0b111: '3D fix',
                      0b110: '2D fix',
                      0b101:'Propagate mode',
                      0b100: 'Position hold',
                      0b011: 'Acquiring satellites',
                      0b010: 'Bad geometry',
                      0b001: 'Reserved',
                      0b000: 'Reserved',
                      }
            out['fixstatus'] = fstats[fix]
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
        elif rtype == "Eq":
            out = {'code': rtype,
                   'info': 'ASCII Position Message',
                   }
            out['response'] = resp[4:-3]
            return out

    def pprint(self, query):
        response = self.ask(query)
        data = self.parse(response)
        print "%s (%s):" %(data['info'], data['code'])
        print "="*20
        del(data['info'])
        del(data['code'])
        deepprint(data)

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

    gps.pprint("Ha"+chr(0))
    print

    # gps.pprint("Hb"+chr(0))

    # print gps.ask("AM"+chr(255)+chr(255)+chr(255)+chr(255))
    # gps.write("AP"+chr(0))
    # print gps.parse(gps.ask("AP"+chr(255)))

    # gps.write("Gd"+chr(3))

    gps.pprint("Gd"+chr(255))
    print
    gps.pprint("Ge"+chr(255))
    print
    ##### print gps.ask("Eq"+chr(0))
