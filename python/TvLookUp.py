#!/usr/bin/python
__author__ = 'kai'
__version__ = '1.0'
__date__ = '6-Apr-2015'

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


def check_irdb(cnx, fmt, val):
    try:
        query = ("SELECT brandname, devicetype, a.codesetid, functionname, count(*) "
                 "FROM uesidfunctionmap a, codesets b, uescodes c, devicetypes d, brands e, functions f "
                 "WHERE a.codesetid = b.codesetid AND a.uesid = c.uesid "
                 "AND a.activeflag = 'Y' AND b.activeflag = 'Y' "
                 "AND d.devicetypeid = b.devicetypeid AND e.brandid = b.brandid AND a.functionid = f.id "
                 #"AND a.functionid = %d AND c.format = '%s' AND c.encodedbinary2 LIKE '%s%%' "
                 "AND c.encodedbinary2 LIKE '%s%%' "
                 "GROUP BY b.brandid, b.devicetypeid, a.functionid " % val)
        #print query
        cnx.cursor.execute(query)
        return cnx.cursor.fetchall()

    except Exception, e:
        print 'check_irdb: %s' % e
        return []


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
def main(timeout=1000):
    log = irutils.Logger('tv')
    cnx = irutils.DBConnection()
    log.out.write('Function ID|Funtion Name|Brand|Type|Codesets|Total Found\n')
    try:
        (fmt, val) = yg_read(log, 'Power', timeout)
        if fmt is not None and val is not None:
            frame = val.split('-', 1)[0].rstrip()
            print ('Check for "%s"...' % frame)
            sets = check_irdb(cnx, fmt, frame)
            print('Name\t|Brand\t|Type\t|Codesets\t|Total Found')
            for each in sets:
                log.out.write('%s|%s|%s|%d|%d\n' % (each[3], each[0], each[1], each[2], each[4]))
                print('%s\t|%s\t|%s\t|%d\t|%d' % (each[3], each[0], each[1], each[2], each[4]))
        else:
            print 'YG920 read failed.\n'

    except Exception, e:
        log.write('lookup: %s\n' % e)

if __name__ == '__main__':
     main()