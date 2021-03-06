#!/usr/bin/python
__author__ = 'kai'
__version__ = '1.0'
__date__ = '10-Mar-2015'

import sys
import time
from utils import irutils
from utils import ygutils


def get_func_by_id(cnx, keyid):
    try:
        query = ('SELECT functionname FROM functions WHERE id = %d ' % keyid)
        cnx.cursor.execute(query)
        func = cnx.cursor.fetchone()
        return func[0]

    except Exception, e:
        print 'get_func_by_id: %s' % e
        return None


def yg_read(log, func, timeout):
    try:
        th = ygutils.Listener(timeout=timeout)
        th.daemon = True
        th.start()
        print 'Please press \"%s\" key...' % func
        while th.isAlive():
            time.sleep(0.1)
        th.join()
        if len(th.data_full_code) > 0:
            log.write('recv \"%s\", \"%s\".\n' % (th.data_format, th.data_full_code))
            return th.data_format, th.data_full_code

    except Exception, e:
        log.write('yg_read: %s\n' % e)
        return None, None


def check_irdb(cnx, keyid, fmt, val):
    try:
        query = ("SELECT brandname, devicetype, a.codesetid, count(*) "
                 "FROM uesidfunctionmap a, codesets b, uescodes c, devicetypes d, brands e "
                 "WHERE a.codesetid = b.codesetid AND a.uesid = c.uesid "
                 "AND a.activeflag = 'Y' AND b.activeflag = 'Y' "
                 "AND d.devicetypeid = b.devicetypeid AND e.brandid = b.brandid "
                 #"AND a.functionid = %d AND c.format = '%s' AND c.encodedbinary2 LIKE '%s%%' "
                 "AND a.functionid = %d AND c.encodedbinary2 LIKE '%s%%' "
                 "GROUP BY b.brandid "
                 % (keyid, val))
        print query
        cnx.cursor.execute(query)
        return cnx.cursor.fetchall()

    except Exception, e:
        print 'check_irdb: %s' % e
        return []


def lookup(keyid=23, timeout=1000):
    log = irutils.Logger('lu')
    cnx = irutils.DBConnection()
    log.out.write('Function ID|Funtion Name|Brand|Type|Codesets|Total Found\n')
    try:
        func = get_func_by_id(cnx, keyid)
        (fmt, val) = yg_read(log, func, timeout)
        if fmt is not None and val is not None:
            frame = val.split('-', 1)[0].rstrip()
            print ('Check for "%s"...' % frame)
            codesets = check_irdb(cnx, keyid, fmt, frame)
            print('ID\t|Name\t|Brand\t|Type\t|Codesets\t|Total Found')
            for each in codesets:
                log.out.write('%d|%s|%s|%s|%d|%d\n' % (keyid, func, each[0], each[1], each[2], each[3]))
                print('%d\t|%s\t|%s\t|%s\t|%d\t|%d' % (keyid, func, each[0], each[1], each[2], each[3]))
        else:
            print 'YG920 read failed.\n'

    except Exception, e:
        log.write('lookup: %s\n' % e)

if __name__ == '__main__':
    try:
        funcid = sys.argv[1:]
        lookup(int(funcid[0]))
    except Exception, x:
        print 'usage: python irlookup.py keyid'
        print '    keyid - function key id (power := 23, chan_up := 15, vol_up := 13).\n'
        print x