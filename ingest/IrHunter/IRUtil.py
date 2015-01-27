# -*- coding:utf-8 -*-

import serial
import threading
import glob

#class IRUtilities(threading.Thread):
class IRUtilities():
    
    def __init__(self):
        #threading.Thread.__init__(self)
        #devlist=glob.glob('/dev/tty.usbserial*')
        #if not devlist:
        #    devlist=glob.glob('/dev/tty.wch*')
        #self.port=devlist[0]
        self.port="COM5"
        print self.port
        self.data=""
        self.ser=serial.Serial(self.port,9600,parity=serial.PARITY_NONE)
        if self.ser.isOpen():
            self.ser.close()
        self.ser.open()
    
    def run(self):
        print "listening"
        self.data=self.readfromserial()
        return self.data
        
    def readfromserial(self):
        counter=0
        try:
            char=' '
            line='##'
            while (ord(char) <> 13):
                try:
                    char=self.ser.read()
                    if char <> '\x00':
                        line=line+char
                except Exception,e:
                    print e
    
            line=line+"\n"
            #self.ser.close()
            return self.decodeGCIRL(line)
        except Exception,e:
            print e
            #self.ser.close()
            
    def decodeGCIRL(self,irstring):
        codedict=dict([(0,''),(1,''),(2,''),(3,''),(4,''),(5,''),(6,'')])
        varcounter=0
        coupleend=0
        intcounter=-1
        couplestring=''
        oldchar=''
        frequency=irstring.split(",")[1]
        for eachchar in irstring[14:]:
           
            if (eachchar=="," or ( ord(eachchar) > 60 and ord(oldchar) < 60)):
                if ord(eachchar) <60:
                    intcounter+=1
                if intcounter%2==0:
                    codedict[coupleend]=couplestring
                    couplestring=''
                    coupleend+=1
            if ord(eachchar) <60:
                couplestring+=eachchar
    
            oldchar=eachchar
        fullstring=''
        for eachchar in irstring[14:]:
            if eachchar=='A' and codedict[1] <> '':
                fullstring+=codedict[1]
            elif eachchar=='B' and codedict[2] <> '':
                fullstring+=codedict[2]
            elif eachchar=='C' and codedict[3] <> '':
                fullstring+=codedict[3]
            elif eachchar=='D' and codedict[4] <> '':
                fullstring+=codedict[4]
            elif eachchar=='E' and codedict[5] <> '':
                fullstring+=codedict[5]
            elif eachchar=='F' and codedict[6] <> '':
                fullstring+=codedict[6]
            else:
                fullstring+=eachchar
            #print fullstring
        return frequency,fullstring[1:].strip()
