#!/usr/bin/python
__author__ = 'kai'
__version__ = '1.0'
__date__ = '2015-11-04'
import datetime
from utils import irutils as ir
from utils import pulsegen as gen
IRDBV1 = "175.41.143.31"  # production
IRDBV2 = "54.251.240.47"  # secured production
IRDBSG = "54.254.101.29"  # staging


def test_codeset(log, irdb, irgen, codeset):
    try:
        sql = ('SELECT a.uesid, a.format, a.encodedbinary2, b.functionid, c.functionname FROM uescodes a '
               '  JOIN uesidfunctionmap b ON b.uesid=a.uesid '
               '  JOIN functions c ON c.id=b.functionid '
               '  WHERE b.codesetid=%d and b.activeflag="Y"; '
               % codeset)
        irdb.cursor.execute(sql)
        rows = irdb.cursor.fetchall()

        fmt = rows[0][1]
        enc = irgen.encoder(fmt)
        for ea in rows:
            encoded_binary = ea[2]
            frequency, repeat_count, main_frame, repeat_frame, toggle_frame = irgen.build(enc, encoded_binary)
            log.out.write('%d|%s|%s|%d|%s|%d|%d\n' % (ea[0], fmt, ea[2], ea[3], ea[4], frequency, repeat_count))
            log.out.write(','.join(map(str, main_frame)))
            log.out.write('\nrepeat:\n')
            log.out.write(','.join(map(str, repeat_frame)))
            log.out.write('\ntoggle:\n')
            log.out.write(','.join(map(str, toggle_frame)))
            log.out.write('\n')
    except Exception, e:
        print e


def test_pulse(irdb, irgen, fmt):
    try:
        enc = irgen.encoder(fmt)
        sql = ("SELECT uesid, encodedbinary2 FROM uescodes WHERE format ='%s' GROUP BY uesid LIMIT 1; " % fmt)
        irdb.cursor.execute(sql)
        rows = irdb.cursor.fetchall()
        for ea in rows:
            encoded_binary = ea[1]
            frequency, repeat_count, main_frame, repeat_frame, toggle_frame = irgen.build(enc, encoded_binary)
            print main_frame, '\n', repeat_frame

    except Exception, e:
        print 'check_irdb: %s' % e


def test():
    log = ir.Logger("hydra")
    v2 = ir.DBConnection()
    hy = gen.Hydra(host='127.0.0.1')

    start_time = datetime.datetime.now()
    print "Started: %s." % start_time

    #test_codeset(log, v2, hy, 100012)
    test_codeset(log, v2, hy, 180131)
    #test_pulse(v2, hy, 'RC-5x') 'uPD6121G

    end_time = datetime.datetime.now()
    print "Duration: from %s to %s (%s)." % (start_time, end_time, (end_time - start_time))


if __name__ == '__main__':
    test()