import simplejson
import urllib2
import serial
import os
import threading
import glob
import time
import socket
from time import strftime
import traceback
import sys
from datetime import datetime
g_isMac = False

PULSE_ERR_SIZE = 3
PULSE_ERR_RATIO = 10

class IRUtilities(threading.Thread):
    def __init__(self):
        global g_isMac
        threading.Thread.__init__(self)
        if sys.platform == 'darwin':
            g_isMac = True
            devlist = glob.glob('/dev/tty.usbserial-*')
            self.port = devlist[0]
            print self.port
        else:
            g_isMac = False
        self.data = ""

    def run(self):
        print "listening"
        self.data = self.readfromserial()
        print "listening done"
        return self.data

    def readfromserial(self):
        global g_isMac
        if g_isMac:
            ser = serial.Serial(self.port, 9600, parity=serial.PARITY_NONE, timeout=10)
        else:
            ser = serial.Serial("COM7", 9600, parity=serial.PARITY_NONE, timeout=10)
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
                    print "while ord: "
                    print e
            line += "\n"
            ser.close()
            return self.decodeGCIRL(line)
        except Exception, e:
            print "readfromserial: "
            print e
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
        return frequency, fullstring[1:]


def getIRStream(uesid):
    headers = {'User-Agent': "Peel"}
    req = "http://samsungir.peel.com/targets/uesid/%d" % uesid
    request = urllib2.Request(req, headers=headers)
    response = urllib2.urlopen(request)
    uesdata = simplejson.loads(response.read())
    return uesdata


def main():
    try:
        timestampsuffix = strftime("%Y%m%d%H%M%S")

        logfilename = "log_%s.txt" % (timestampsuffix)
        logfile = open(logfilename, 'w')
        start_time = datetime.now()
        print "Started: %s" %  start_time
        logfile.write("Started: %s\n" % start_time)

        csvfilename = "checks_%s.csv" % (timestampsuffix)
        csvfile = open(csvfilename, 'w')
        csvfile.write("UESID,Fail to Send,Pass,Freq Error,Pulse Error (> %d%%),Pulse Warning (> %d)\n" % (PULSE_ERR_RATIO, PULSE_ERR_SIZE))

        # 3rd party verification test set
        #uesidlist=[1]
        #uesidlist=[203365, 204224, 244841]
        uesidlist=[1, 29, 132, 169, 200, 226, 312, 351, 417, 435, 477, 543, 606, 673, 688, 713, 738, 812, 837, 862, 887, 913, 939, 1024, 1050, 1091, 1127, 1154, 1207, 1237, 1267, 1297, 1331, 1361, 1395, 1420, 1453, 1492, 1519, 1546, 1572, 1597, 1622, 1685, 1708, 1732, 1757, 1809, 1834, 1859, 1913, 1966, 1998, 2027, 2042, 2056, 2118, 2212, 2234, 2256, 2276, 2309, 2340, 2368, 2398, 2419, 2451, 2480, 2502, 2521, 2540, 2562, 2593, 2613, 2634, 2663, 2687, 2707, 2727, 2747, 2767, 2781, 2834, 2850, 2903, 2919, 2935, 2951, 2969, 2985, 3002, 3018, 3033, 3049, 3065, 3086, 3100, 3132, 3148, 3165, 3180, 3197, 3213, 3269, 3289, 3305, 3324, 3344, 3364, 3401, 3417, 3477, 3493, 3509, 3525, 3540, 3556, 3572, 3587, 3603, 3617, 3632, 3665, 3681, 3697, 3713, 3727, 3744, 3760, 3777, 3793, 3827, 3861, 3912, 3933, 3950, 3967, 3984, 4001, 4018, 4034, 4049, 4066, 4083, 4099, 4117, 4152, 4168, 4189, 4205, 4222, 4236, 4256, 4277, 4326, 4352, 4357, 4382, 4395, 4426, 4461, 4546, 4662, 4731, 4763, 4781, 4817, 4853, 4877, 4912, 4967, 4990, 5040, 5054, 5095, 5142, 5166, 5295, 5311, 5327, 5344, 5360, 5406, 5479, 5511, 5526, 5542, 5590, 5604, 5628, 5653, 5671, 5689, 5706, 5727, 5804, 5826, 5848, 5911, 5927, 5958, 5963, 5974, 5983, 6008, 6035, 6069, 6084, 6098, 6148, 6157, 6165, 6195, 6205, 6214, 6227, 6240, 6251, 6293, 6325, 6338, 6357, 6371, 6402, 6409, 6418, 6428, 6479, 6496, 6500, 6521, 6536, 6562, 6574, 6587, 6625, 6650, 6661, 6678, 6700, 6727, 6740, 6751, 6760, 6765, 10147, 10167, 10184, 10202, 10220, 10238, 10256, 10274, 10292, 10310, 10328, 10346, 10364, 10382, 10400, 10489, 10697, 10736, 10771, 10865, 20045, 20073, 20137, 20174, 20194, 20298, 20580, 20633, 20702, 20805, 20908, 20934, 21021, 21141, 21338, 21367, 21390, 21692, 21769, 22656, 22860, 22959, 22992, 23279, 23773, 23949, 24215, 24252, 24610, 24703, 24898, 24998, 25764, 26769, 27359, 27715, 27741, 27759, 27933, 28067, 28353, 28457, 28908, 28986, 100762, 101555, 102116, 102271, 102379, 102411, 102872, 103364, 103543, 105911, 107321, 108846, 109323, 109742, 110135, 110225, 110256, 111725, 112744, 112957, 113151, 113688, 113894, 114118, 114434, 114624, 115149, 115662, 116285, 116693, 117395, 118262, 122431, 128034, 131192, 133151, 136465, 140525, 141455, 141527, 146972, 147016, 151341, 154386, 154564, 155329, 159014, 160753, 162539, 163292, 166015, 177320, 178172, 178528, 178615, 179244, 180441, 181549, 181585, 181660, 181773, 181817, 181882, 182012, 182036, 182062, 182087, 182111, 182139, 182164, 188588, 191372, 191471, 197479, 197528, 197579, 202142, 202169, 202294, 202998, 203025, 203078, 203116, 203365, 203463, 203596, 203626, 203807, 203840, 204224, 204321, 204948, 204972, 204996, 205020, 205044, 205068, 205092, 205116, 205140, 205188, 205212, 205236, 205260, 205284, 205308, 205332, 205356, 205380, 205428, 205452, 205476, 205500, 205524, 205548, 205572, 205620, 205644, 205668, 205692, 205716, 205740, 205788, 205812, 205836, 205860, 205908, 205932, 205956, 206004, 206028, 206052, 206076, 206100, 206124, 206148, 206220, 206244, 206292, 206316, 206340, 206364, 206388, 206436, 206460, 206508, 206532, 206556, 206580, 206652, 206700, 206724, 206748, 206772, 206796, 206844, 206892, 206916, 206940, 206964, 206988, 207012, 207036, 207060, 207084, 207132, 207156, 207180, 207204, 207228, 207252, 207276, 207372, 207420, 207444, 207516, 207540, 207564, 207588, 207678, 207868, 207895, 207922, 207981, 208341, 208389, 210377, 214598, 215295, 215540, 216077, 222097, 222106, 222157, 223096, 224979, 225031, 225347, 227854, 229659, 229707, 229752, 229841, 230118, 230177, 230237, 230297, 230418, 230460, 231040, 231709, 231762, 232253, 232337, 232681, 232823, 233540, 234171, 234463, 234894, 234904, 234992, 235081, 235135, 235189, 235367, 235591, 236025, 243062, 243747, 244841, 245194, 245242, 245285, 245683, 245834, 245920, 245975]
        #uesidlist=[1, 29, 132, 169, 200, 226, 312, 351, 417, 435, 477, 543, 606, 673, 688, 713, 738, 812, 837, 862, 887, 913, 939, 1024, 1050, 1091, 1127, 1154, 1207, 1237, 1267, 1297, 1331, 1361, 1395, 1420, 1453, 1492, 1519, 1546, 1572, 1597, 1622, 1685, 1708, 1732, 1757, 1809, 1834, 1859, 1913, 1966, 1998]
        workedues = []
        frequencyFailures = []
        pulsePoor = []
        pulseFailures = []
        readFailures = []
        pulseFailures2 = []

        for uesid in uesidlist:
            try:
                print "Checking UESID %d ..." % uesid
                csvfile.write("%d," % uesid)

                uesdata = getIRStream(uesid)
                cloudfrequency = int(uesdata["frequency"])
                cloudirdata = uesdata["mainframe"].split(" ")
                if len(cloudirdata) <= 1:
                    print "try toggle frame..."
                    cloudirdata = uesdata["toggleframe1"].split(" ")

                adbthread = IRUtilities()
                adbthread.start()
                time.sleep(2)

                #sendadb_rooted_s4(cloudfrequency, cloudirdata)
                #sendadb_smartircmd(cloudfrequency, cloudirdata)
                send_cir_adb(cloudfrequency, cloudirdata)

                adbthread.join()
                (phonefrequencyc, phoneirdata) = adbthread.data

                print
                print "__________________________"
                print cloudfrequency, ",".join(cloudirdata)
                print phonefrequencyc, phoneirdata
                print "___________________________"
                print

                phonefrequency = int(phonefrequencyc)
                print uesid
                #logfile.write("%d:%d:%s" % (uesid, phonefrequency, phoneirdata))
                print "####"
                #logfile.flush()

                (dataDiffResult, dataDiffResult2) = compareir(cloudirdata, phoneirdata)
                if dataDiffResult == 1:
                    pulsePoor.append(uesid)
                if dataDiffResult == 2:
                    pulseFailures.append(uesid)

                frequencyError = False
                if abs(cloudfrequency - phonefrequency) >= 2000:
                    frequencyFailures.append(uesid)
                    frequencyError = True
                if abs(float(cloudfrequency - phonefrequency) * 100 / float(cloudfrequency)) != 1:
                    print "Frequency: Cloud is %d,phone is %d. Difference is %f %%" % \
                          (cloudfrequency, phonefrequency, float(cloudfrequency - phonefrequency) * 100 / float(cloudfrequency))

                if frequencyError is False and dataDiffResult == 0:
                    # pass
                    csvfile.write(",X,,,")
                    workedues.append(uesid)
                else:
                    csvfile.write(",,")
                    if frequencyError:
                        csvfile.write("X")
                    csvfile.write(",")
                    if dataDiffResult > 0:
                        csvfile.write("X")
                    csvfile.write(",")

                if dataDiffResult2:
                    csvfile.write("X")
                csvfile.write("\n")

            except Exception, e:
                readFailures.append(uesid)
                print "for uesid: "
                print e
                csvfile.write("X,,,,\n")

        csvfile.close()

        end_time = datetime.now()

        logfile.write("Worked: ")
        logfile.write("%s\n" % workedues)
        logfile.write("frequency failures: ")
        logfile.write("%s\n" % frequencyFailures)
        logfile.write("pulse poor: ")
        logfile.write("%s\n" % pulsePoor)
        logfile.write("pulse failures: ")
        logfile.write("%s\n" % pulseFailures)
        logfile.write("read failures: ")
        logfile.write("%s\n" % readFailures)
        logfile.write("Ended: %s\n" % end_time)
        logfile.write("Duration: %s\n" % (end_time - start_time))
        logfile.close()
        print "Worked: "
        print workedues
        print "frequency failures: "
        print frequencyFailures
        print "pulse poor: "
        print pulsePoor
        print "pulse failures: "
        print pulseFailures
        print "read failures: "
        print readFailures
        print "Ended: %s" %  end_time
        print "Duration: %s\n" % (end_time - start_time)

    except Exception, e:
        print "main: "
        print e
        traceback.print_exc()


def sendadb_rooted_s4(frequency, irdata):
    adbcmdprefix = 'adb shell '
    # For rooted s4
    adbcmd = adbcmdprefix + '"echo ' + str(frequency) + "," + ",".join(irdata) + ' > /sys/class/sec/sec_ir/ir_send"'
    print "adb shell command is \n" + adbcmd
    os.popen(adbcmd)


def sendadb_smartircmd(frequency, irdata):
    adbcmdprefix = 'adb shell '
    # For smartircmd (without going thru ConsumerIrManager)
    adbcmd = adbcmdprefix + '/dev/smartircmd ' +  str(frequency) + " " + ",".join(irdata)
    print "adb shell command is \n" + adbcmd
    os.popen(adbcmd)


def send_cir_adb(frequency, irdata):
    adbcmdprefix = 'adb shell '
    cir_file = '/sdcard/irtest.txt'
    adbcmd = adbcmdprefix + '"echo 1,' + str(frequency) + "," + ",".join(irdata) + ' > /sdcard/irtest.txt"'
    print "adb shell command is \n" + adbcmd
    os.popen(adbcmd)
    adbcmd = adbcmdprefix + 'am start -n com.peel.peelkktestapp.app/com.peel.peelkktestapp.app.MainActivity'
    print "adb shell command is \n" + adbcmd
    os.popen(adbcmd)


def compareir(cloudstring, phonestring):
    clouddata = cloudstring
    phonedata = phonestring.split(",")
    foundDataFault = 0
    foundDataFault2 = False

    for eachpulse in range(min(len(clouddata), len(phonedata)) - 1):
        if int(clouddata[eachpulse]) < 800:

            diffpercent = abs((float(clouddata[eachpulse]) - float(phonedata[eachpulse])) * 100 / (float(clouddata[eachpulse])))
            if diffpercent > PULSE_ERR_RATIO:
                print " Difference for pulse %d is %f %% .   %s vs %s" % (eachpulse, diffpercent, clouddata[eachpulse], phonedata[eachpulse])
                if foundDataFault == 0:
                    foundDataFault = 1
                if diffpercent > 25:
                    foundDataFault = 2

            d2 = abs(int(clouddata[eachpulse]) - int(phonedata[eachpulse]))
            if d2 > PULSE_ERR_SIZE:
                print " Difference for pulse %d is %d.   %s vs %s" % (eachpulse, d2, clouddata[eachpulse], phonedata[eachpulse])
                foundDataFault2 = True

    return foundDataFault, foundDataFault2


if __name__ == '__main__':
    main()