__version__ = "3.2.0"
__date__ = "19-Nov-2014"
import threading
import glob
import sys
import serial

COMPORT = 'COM1'

class IRUtilities(threading.Thread):
    isMac = False

    def __init__(self):
        threading.Thread.__init__(self)
        if sys.platform == 'darwin':
            self.isMac = True
            devlist = glob.glob('/dev/tty.usbserial-*')
            self.port = devlist[0]
            print self.port
        self.data = ""

    def run(self):
        #print "listening"
        self.data = self.readfromserial()
        #print "listening done"
        return self.data

    def readfromserial(self):
        if self.isMac:
            ser = serial.Serial(self.port, 9600, parity=serial.PARITY_NONE, timeout=10)
        else:
            print COMPORT
            ser = serial.Serial(COMPORT, 9600, parity=serial.PARITY_NONE, timeout=10)
        if ser.isOpen():
            ser.close()
        ser.open()
        try:
            char = ' '
            line = '##'
            while (ord(char) <> 13):
                try:
                    char = ser.read()
                    if char <> '\x00':
                        line = line + char
                        #print line
                except Exception, e:
                    print "while ord: %s" % e
            line = line + "\n"
            ser.close()
            return self.decodeGCIRL(line)
        except Exception, e:
            print "readfromserial: %s" % e
            ser.close()

    def decodeGCIRL(self, irstring):
        codedict = dict([(0, ''), (1, ''), (2, ''), (3, ''), (4, ''), (5, ''), (6, '')])
        coupleend = 0
        intcounter = -1
        couplestring = ''
        oldchar = ''
        frequency = irstring.split(",")[1]
        for eachchar in irstring[14:]:
            if (eachchar == "," or ( ord(eachchar) > 60 and ord(oldchar) < 60)):
                if ord(eachchar) < 60:
                    intcounter += 1
                if intcounter % 2 == 0:
                    codedict[coupleend] = couplestring
                    couplestring = ''
                    coupleend += 1
            if ord(eachchar) < 60:
                couplestring += eachchar
            oldchar = eachchar
        fullstring = ''
        for eachchar in irstring[14:]:
            if eachchar == 'A' and codedict[1] <> '':
                fullstring += codedict[1]
            elif eachchar == 'B' and codedict[2] <> '':
                fullstring += codedict[2]
            elif eachchar == 'C' and codedict[3] <> '':
                fullstring += codedict[3]
            elif eachchar == 'D' and codedict[4] <> '':
                fullstring += codedict[4]
            elif eachchar == 'E' and codedict[5] <> '':
                fullstring += codedict[5]
            elif eachchar == 'F' and codedict[6] <> '':
                fullstring += codedict[6]
            else:
                fullstring += eachchar
                #print fullstring
        return frequency, fullstring[1:]
