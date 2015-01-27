__version__ = "4.0.0"
__date__ = "05-DEC-2014"
import subprocess
import simplejson
import urllib2
import time
import MySQLdb
import datetime
import pexpect
import os
IRDBV1 = "175.41.143.31"  # production
IRDBV2 = "54.251.240.47"  # secured production
IRDBSG = "54.254.101.29"  # staging


class DBConnection:
    def __init__(self, host=IRDBV2, db="devices", user="zdbadmin", passwd="z3l4yi23"):
        try:
            self.db = MySQLdb.connect(host=host, user=user, passwd=passwd, db=db)
            self.cursor = self.db.cursor()
        except Exception, e:
            print "ERR:DBConnection:__init__: %s" % e

    def __del__(self):
        try:
            #print 'DBConnection:__del__...'
            self.cursor.close()
            self.db.close()
        except Exception, e:
            print "ERR:DBConnection:__del__: %s" % e

    def clear_cache(self):
        query = "SELECT DISTINCT serverip FROM servers "
        try:
            self.cursor.execute(query)
            servers = self.cursor.fetchall()
            for server in servers:
                try:
                    print server[0]
                    telnetcmd = "telnet %s 11211" % (server[0])
                    print telnetcmd
                    child = pexpect.spawn(telnetcmd)
                    matchstring = "Connected to *"
                    child.expect(matchstring)
                    child.sendline('flush_all')
                    child.expect('OK')
                    child.sendline('quit')
                    print "Cache Cleared"
                except Exception, e:
                    print e
        except Exception, e:
            print "ERR:DBConnection:clear_cache: %s" % e


class Logger:
    start_time = None

    def __init__(self, tag):
        time_stamp_suffix = time.strftime("%Y%m%d%H%M%S")
        log_filename = "%sLog%s.txt" % (tag, time_stamp_suffix)
        #err_filename = "%sErr%s.txt" % (tag, time_stamp_suffix)
        self.log = open(log_filename, 'w')
        #self.err = open(err_filename, 'w')
        self.start_time = datetime.datetime.now()
        self.log.write("Started: %s.\n" % self.start_time)

    def __del__(self):
        end_time = datetime.datetime.now()
        self.log.write("Duration: from %s to %s (%s).\n" % (self.start_time, end_time, (end_time - self.start_time)))
        self.log.close()
        #self.err.close()

    def write(self, b):
        self.log.write(b)
        print b


def get_ir_stream(uesid):
    headers = {'User-Agent': "Peel"}
    req = "http://partners-ir.peel.com/targets/uesid/%d" % uesid
    try:
        request = urllib2.Request(req, headers=headers)
        response = urllib2.urlopen(request)
        uesdata = simplejson.loads(response.read())
        return uesdata
    except Exception, e:
        print "ERR:get_ir_stream: %s" % e
        return None


def get_ir_stream2(uesid):
    headers = {'User-Agent': "Peel"}
    req = "http://partners-ir.peel.com/targets/uesid/%d" % uesid
    try:
        request = urllib2.Request(req, headers=headers)
        response = urllib2.urlopen(request)
        uesdata = simplejson.loads(response.read())
        return uesdata
    except Exception, e:
        print "ERR:get_ir_stream: %s" % e
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
        print "ERR:sendadb_rooted_s4: %s" % e


def testadb_rooted_s4(ir_data):
    try:
        adb_cmd = 'echo ' + ir_data + ' > /sys/class/sec/sec_ir/ir_send' + '\r\nexit\r\n'
        pipe = subprocess.Popen(['adb', 'shell'], shell=True, stdin=subprocess.PIPE)
        pipe.communicate(input=adb_cmd)
        return pipe
    except Exception, e:
        print "ERR:sendadb_rooted_s4: %s" % e


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
"""
