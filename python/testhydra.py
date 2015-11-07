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


def test_pulse(irdb, irgen, fmt):
    try:
        enc = irgen.encoder(fmt)
        sql = ("SELECT uesid, encodedbinary2 FROM uescodes WHERE format ='%s' GROUP BY uesid LIMIT 1; " % fmt)
        irdb.cursor.execute(sql)
        rows = irdb.cursor.fetchall()
        for ea in rows:
            encoded_binary = ea[1]
            pulses = irgen.build(enc, encoded_binary)
            print pulses

    except Exception, e:
        print 'check_irdb: %s' % e


def test():
    v2 = ir.DBConnection()
    hy = gen.Hydra(host='127.0.0.1')

    start_time = datetime.datetime.now()
    print "Started: %s." % start_time

    test_pulse(v2, hy, 'SAA3010 RC-5')
    #test_pulse(v2, hy, 'RC-5x')

    end_time = datetime.datetime.now()
    print "Duration: from %s to %s (%s)." % (start_time, end_time, (end_time - start_time))


if __name__ == '__main__':
    test()