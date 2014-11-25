__version__ = "3.1.0"
__date__ = "18-Nov-2014"
import time
import datetime
import traceback
import testset
import irutils
import gcutils
import ygutils
# error threshold
PULSE_ERR_SIZE = 3
PULSE_ERR_RATIO = 10
FREQ_ERR_SIZE = 1000
__USE_GC__ = True
__USE_YG__ = True

def main():
    timestampsuffix = time.strftime("%Y%m%d%H%M%S")

    csvfilename = "irt_%s.csv" % (timestampsuffix)
    csvfile = open(csvfilename, 'w')
    csvfile.write("ID,Code Type,")
    if __USE_GC__:
        csvfile.write("[GC] Fail to Send,[GC] Pass,[GC] Freq Error(>%d),[GC] Pulse Error(>%d%%),[GC] Pulse Warning(>%d)" % (FREQ_ERR_SIZE, PULSE_ERR_RATIO, PULSE_ERR_SIZE))
    if __USE_YG__:
        csvfile.write("[YG] Fail to Send,[YG] Pass,[YG] Pulse Error(>%d%%),[YG] Pulse Warning(>%d)" % (PULSE_ERR_RATIO, PULSE_ERR_SIZE))
    csvfile.write('\n')

    logfilename = "irt_%s.txt" % (timestampsuffix)
    logfile = open(logfilename, 'w')
    start_time = datetime.datetime.now()

    workedues = []
    frequencyFailures = []
    pulsePoor = []
    pulseFailures = []
    readFailures = []
    networkFailures = []

    try:
        n = 0
        for eachuesid in testset.uesidlist:
            uesid = eachuesid
            n += 1
            print "\nChecking %dth UESID=%d ..." % (n, uesid)
            uesdata = irutils.getIRStream(uesid)
            if uesdata is not None:
                csvfile.write("%d" % uesid)
                logfile.write("\n<UESID=%d\n" % uesid)
                try:
                    type = "Full_Repeat"
                    cloudfrequency = int(uesdata["frequency"])
                    cloudirmain = uesdata["mainframe"].split(" ")
                    if len(cloudirmain) <= 1:
                        print "try toggle frame..."
                        type = "Toggle"
                        cloudirmain = uesdata["toggleframe1"].split(" ")
                    cloudirrpt = uesdata["repeatframe"].split(" ")
                    if len(cloudirrpt) <= 1:
                        type = "Partial_Repeat"
                    #cloudirdata = irutils.build_pulses(1, cloudirmain, cloudirrpt)
                    cloudirdata = irutils.build_pulses(int(uesdata["repeatcount"]), cloudirmain, cloudirrpt)
                    csvfile.write(",%s" % type)

                    if __USE_GC__:
                        gcthread = gcutils.IRUtilities()
                        gcthread.start()
                    if __USE_YG__:
                        ygthread = ygutils.Listener(cloudfrequency)
                        ygthread.start()

                    # wait for gc-irl power up.
                    time.sleep(2)
                    irutils.sendadb_rooted_s4(cloudfrequency, cloudirdata)
                    #send_cir_ios("C:/log/uesid.txt", uesid)

                    print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
                    print ">SEND>|", cloudfrequency, '|', ','.join(cloudirdata)
                    logfile.write("SEND|%d|%s\n" % (cloudfrequency, ','.join(cloudirdata)))

                    if __USE_GC__:
                        gcthread.join()
                        if gcthread.data:
                            (gcfrequencyc, gcirdata) = gcthread.data
                            gcfrequency = int(gcfrequencyc)
                            print "GC-IRL|", gcfrequency, '|', gcirdata
                            logfile.write("GC-IRL|%d|%s\n" % (gcfrequency, gcirdata))
                        else:
                            gcirdata = None
                    if __USE_YG__:
                        ygthread.join()
                        if len(ygthread.data_wave_buf):
                            ygirdata = ",".join(map(str, ygthread.data_wave_buf))
                            ygfrequency = ygthread.data_wave_freq
                            print "YG-920|", ygfrequency, '|', ygirdata
                            logfile.write("YG-920|%d|%s\n" % (ygfrequency, ygirdata))
                        else:
                            ygirdata = None

                    # wait for gc-irl closing serial port..
                    time.sleep(1)
                    print "<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"

                    if __USE_GC__:
                        if gcirdata:
                            (diff_percent, diff_size) = compareir(logfile, cloudirdata, gcirdata)
                            diff_freq = abs(cloudfrequency - gcfrequency)
                            if diff_size > 0:
                                pulsePoor.append(uesid)
                            if diff_percent > 0:
                                pulseFailures.append(uesid)
                            if diff_freq > FREQ_ERR_SIZE:
                                frequencyFailures.append(uesid)
                                logfile.write("[GC] Frequency: Cloud is %d,phone is %d. Difference is %f %%\n" % (cloudfrequency, gcfrequency, float(cloudfrequency - gcfrequency) * 100 / float(cloudfrequency)))
                            if (diff_freq <= FREQ_ERR_SIZE) and (diff_percent <= PULSE_ERR_RATIO) and (diff_size <= PULSE_ERR_SIZE):
                                # pass
                                csvfile.write(",,X,,,")
                                workedues.append(uesid)
                            else:
                                csvfile.write(",,,")
                                if diff_freq > FREQ_ERR_SIZE:
                                    csvfile.write("%d" % diff_freq)
                                csvfile.write(",")
                                if diff_percent > PULSE_ERR_RATIO:
                                    csvfile.write("%d" % diff_percent)
                                csvfile.write(",")
                                if diff_size > PULSE_ERR_SIZE:
                                    csvfile.write("%d" % diff_size)
                        else:
                            readFailures.append(uesid)
                            csvfile.write(",X,,,,")

                    if __USE_YG__:
                        if ygirdata:
                            (diff_percent, diff_size) = compareir(logfile, cloudirdata, ygirdata)
                            if diff_size > 0:
                                pulsePoor.append(uesid)
                            if diff_percent > 0:
                                pulseFailures.append(uesid)
                            if (diff_percent <= PULSE_ERR_RATIO) and (diff_size <= PULSE_ERR_SIZE):
                                # pass
                                csvfile.write(",,X,,")
                                workedues.append(uesid)
                            else:
                                csvfile.write(",,,")
                                if diff_percent > PULSE_ERR_RATIO:
                                    csvfile.write("%d" % diff_percent)
                                csvfile.write(",")
                                if diff_size > PULSE_ERR_SIZE:
                                    csvfile.write("%d" % diff_size)
                        else:
                            readFailures.append(uesid)
                            csvfile.write(",X,,,")

                        csvfile.write("\n")
                        csvfile.flush()
                        logfile.write("/>\n")
                        logfile.flush()

                except Exception, e:
                    print "for UESID=%d: %s." % (uesid, e)
            else:
                networkFailures.append(uesid)

        csvfile.close()
        end_time = datetime.datetime.now()
        logfile.write("Worked: %s\n" % workedues)
        logfile.write("frequency failures: %s\n" % frequencyFailures)
        logfile.write("pulse poor: %s\n" % pulsePoor)
        logfile.write("pulse failures: %s\n" % pulseFailures)
        logfile.write("read failures: %s\n" % readFailures)
        logfile.write("Duration: %s\n" % (end_time - start_time))
        logfile.close()

    except Exception, e:
        print "main: %s" % e
        traceback.print_exc()


def compareir(log, cloud_string, phone_string):
    clouddata = cloud_string
    phonedata = phone_string.split(",")
    diff_percent = 0
    diff_size = 0
    for eachpulse in range(min(len(clouddata), len(phonedata)) - 1):
        if int(clouddata[eachpulse]) < 800:
            d = int(abs((float(clouddata[eachpulse]) - float(phonedata[eachpulse])) * 100.0 / (float(clouddata[eachpulse]))))
            if d > PULSE_ERR_RATIO:
                log.write("Difference for pulse %d is %d%% .   %s vs %s\n" % (eachpulse, d, clouddata[eachpulse], phonedata[eachpulse]))
                if d > diff_percent:
                    diff_percent = d
            d = abs(int(clouddata[eachpulse]) - int(phonedata[eachpulse]))
            if d > PULSE_ERR_SIZE:
                log.write("Difference for pulse %d is %d.   %s vs %s\n" % (eachpulse, d, clouddata[eachpulse], phonedata[eachpulse]))
                if d > diff_size:
                    diff_size = d
    return diff_percent, diff_size

if __name__ == '__main__':
    main()