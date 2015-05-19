import time
from utils import irutils
#from utils import gcutils
from utils import ygutils
# error threshold
PULSE_ERR_SIZE = 3
PULSE_ERR_RATIO = 10
FREQ_ERR_SIZE = 1000
"""
UESFREQUENCY = 38000
UESMAINFRAME = ("171,170,21,63,21,63,21,63,21,21,21,21,21,21,21,21,21,21,21,63,21,63,21,63,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,63,21,63,21,21,21,21,21,63,21,63,21,63,21,63,21,21,21,21,21,63,21,63,21,21,21,1771,"
                "171,170,21,63,21,63,21,63,21,21,21,21,21,21,21,21,21,21,21,63,21,63,21,63,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,63,21,63,21,21,21,21,21,63,21,63,21,63,21,63,21,21,21,21,21,63,21,63,21,21,21,1771,"
                "171,170,21,63,21,63,21,63,21,21,21,21,21,21,21,21,21,21,21,63,21,63,21,63,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,21,63,21,63,21,21,21,21,21,63,21,63,21,63,21,63,21,21,21,21,21,63,21,63,21,21,21,3800")
"""
UESFREQUENCY = 38000
UESMAINFRAME = "346,170,23,18,23,18,22,62,22,62,23,18,23,18,23,18,23,18,22,62,22,62,23,18,22,62,22,62,22,62,22,62,22,62,23,18,22,62,23,18,23,18,23,18,23,18,23,18,23,18,22,62,23,18,22,62,22,62,22,62,22,62,22,62,22,62,22,1500,342,86,21,3800"


def main():
    try:
        cloudfrequency = UESFREQUENCY
        cloudirmain = UESMAINFRAME.split(',')
        cloudirdata = irutils.build_pulses(1, cloudirmain, None)

        ygthread = ygutils.Listener(cloudfrequency)
        ygthread.start()

        # wait for gc-irl power up.
        time.sleep(2)
        irutils.sendadb_rooted_s4(cloudfrequency, cloudirdata)
        #send_cir_ios("C:/log/uesid.txt", uesid)

        ygthread.join()
        if len(ygthread.data_wave_buf):
            ygirdata = ",".join(map(str, ygthread.data_wave_buf))
            ygfrequency = ygthread.data_wave_freq
            print "YG-920|", ygfrequency, '|', ygirdata
            #logfile.write("YG-920|%d|%s\n" % (ygfrequency, ygirdata))
        else:
            ygirdata = None

    except Exception, e:
        print e


if __name__ == '__main__':
    main()
