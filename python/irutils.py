__version__ = "3.2.0"
__date__ = "19-Nov-2014"
import subprocess
import simplejson
import urllib2

def getIRStream(uesid):
    headers = {'User-Agent': "Peel"}
    req = "http://samsungir.peel.com/targets/uesid/%d" % uesid
    try:
        request = urllib2.Request(req, headers=headers)
        response = urllib2.urlopen(request)
        uesdata = simplejson.loads(response.read())
        return uesdata
    except Exception, e:
        print "ERR:getIRStream: %s" % e
        return None


def build_pulses(repeat_cnt, ir_data, ir_repeat):
    adb_ir_data = ir_data
    if ir_repeat and len(ir_repeat) > 1:
        adb_ir_data += ir_repeat
        adb_ir_rep = ir_repeat
    else:
        adb_ir_rep = ir_data
    for i in range(repeat_cnt - 1):
        adb_ir_data += adb_ir_rep
    return adb_ir_data


def sendadb_rooted_s4(frequency, ir_data):
    try:
        adb_cmd = 'echo ' + str(frequency) + ',' + ','.join(ir_data) + ' > /sys/class/sec/sec_ir/ir_send' + '\r\nexit\r\n'
        pipe = subprocess.Popen(['adb', 'shell'], shell=True, stdin=subprocess.PIPE)
        pipe.communicate(input=adb_cmd)
        return pipe
    except Exception, e:
        print "ERR:sendadb_rooted_s4:%s" % e

"""
def sendadb_ios_http(filename, uesid):
    try:
        os.remove(filename)
    except OSError:
        pass
    out = open(filename, 'w')
    out.write('%d' % uesid)
    out.close()


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
"""
