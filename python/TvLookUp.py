#!/usr/bin/python
__author__ = 'kai'
__version__ = '1.0'
__date__ = '6-Apr-2015'

import time
from utils import irutils
from utils import ygutils

device_types = {'tv': 1, 'stb': 2, 'dvd': 3, 'av': 5, 'audio': 5, 'smp': 6, 'iptv mp': 6, 'prj': 10, 'ac': 18, 'vcr': 21}
key_sequence = [['Power', '23, 48, 332'],
                ['Right>', '32'], ['OK/Select', '11, 28, 330'],
                ['Menu', '27'], ['Input/Source', '25, 190'],
                ['Vol+ (Up)', '13'], ['Mute', '12'],
                ['Ch+ (Up)', '15'], ['8', '9']]
DEVICE_TYPE_ID = device_types['tv']
codeset_counter = 0


def yg_read(log, func, timeout):
    try:
        th = ygutils.Listener(timeout=timeout)
        th.daemon = True
        th.start()
        log.write('Please press \"%s\" key...' % func)
        while th.isAlive():
            time.sleep(0.1)
        th.join()
        if len(th.data_full_code) > 0:
            log.log.write('Received format:\"%s\", value:\"%s\".\n' % (th.data_format, th.data_full_code))
            return th.data_format, th.data_full_code
    except Exception, e:
        log.write('yg_read: %s' % e)
        return None, None


def check_irdb(cnx, func_id, val, sets):
    codesets = []
    cond = ''
    if len(sets) > 0:
        cond = ' AND a.codesetid IN ('
        for each in sets:
            cond += str(each)
            cond += ','
        cond = cond[:-1]
        cond += ') '
    try:
        query = ("SELECT a.codesetid "
                 "FROM uesidfunctionmap a, codesets b, uescodes c "
                 "WHERE a.codesetid=b.codesetid AND a.uesid=c.uesid "
                 "AND a.activeflag='Y' AND b.activeflag='Y' "
                 "AND c.encodedbinary2 LIKE '%s%%' AND a.functionid IN (%s) %s "
                 "GROUP BY b.brandid, b.devicetypeid " % (val, func_id, cond))
        cnx.cursor.execute(query)
        return cnx.cursor.fetchall()
    except Exception, e:
        print 'check_irdb: %s' % e
        return []


def check_key(log, cnx, key_name, key_id, codesets, timeout):
    found = []
    try:
        (fmt, val) = yg_read(log, key_name, timeout)
        if fmt is not None and val is not None:
            frame = val.split('-', 1)[0].rstrip()
            log.log.write('Searching for "%s"...\n' % frame)
            sets = check_irdb(cnx, key_id, frame, codesets)
            for each in sets:
                found.append(each[0])
        else:
            log.write('YG920 read %s failed.' % key_name)
        return found

    except Exception, e:
        log.write('check_key: %s' % e)
        return found

# check for key groups
# power: power, poweron, power_off
# ch: ch+, ch-
# num: 1-9
# vol: vol+, vol-, mute
# input/source
# nav+select/ok
# enter
# menu
# info
# return/back, exit
# last/pre-ch
def check_codeset(log, cnx, timeout):
    codesets = []
    try:
        for each in key_sequence:
            codesets = check_key(log, cnx, each[0], each[1], codesets, timeout)
            if len(codesets) > 0:
                log.write('%d codesets found.' % len(codesets))
            else:
                return codesets
        return codesets
    except Exception, e:
        log.write('check_codeset: %s' % e)
        return codesets


def print_duplicates(log, cnx, seq, codesets):
    cond = ''
    try:
        if len(codesets) > 0:
            cond = ' AND a.codesetid IN ('
            for each in codesets:
                cond += str(each)
                cond += ','
            cond = cond[:-1]
            cond += ') '

            query = ("SELECT c.devicetype, b.brandname, a.codesetid, a.rank, count(*) "
                     "FROM codesets a, brands b, devicetypes c "
                     "WHERE a.brandid=b.brandid AND a.devicetypeid=c.devicetypeid %s "
                     "GROUP BY a.brandid, a.devicetypeid "
                     "ORDER BY a.rank " % cond)
            cnx.cursor.execute(query)
            founds = cnx.cursor.fetchall()

            for each in founds:
                row = '%d|%s|%s|%d|%d|%d' % (seq, each[0], each[1], each[2], each[3], each[4])
                log.out.write('%s\n' % row)
                log.write(row)
            log.out.flush()
            log.log.flush()

    except Exception, e:
            print 'print_duplicates: %s' % e


def test_loop(log, cnx, timeout):
    global codeset_counter
    try:
        while True:
            codeset_counter += 1
            log.write('\nChecking remote #%d ...' % codeset_counter)
            codesets = check_codeset(log, cnx, timeout)
            print_duplicates(log, cnx, codeset_counter, codesets)

    except Exception, e:
        log.write('test_loop: %s\n' % e)


def main(timeout=1000):
    log = irutils.Logger('tv')
    cnx = irutils.DBConnection()
    log.out.write('TestNo|DeviceType|BrandName|Codesets|Rank|CodesetCount\n')
    test_loop(log, cnx, timeout)

if __name__ == '__main__':
    main()