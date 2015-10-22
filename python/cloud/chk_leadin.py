#!/usr/bin/python
from utils import irutils as ir
__author__ = 'kai'
__version__ = '1.0'
__date__ = '18-Sep-2015'


def prt_format_leadin(log, cnx):
    try:
        query = ("SELECT a.format, b.seq, b.pulse, count(*) FROM uescodes a "
                 "JOIN uespulses b ON b.uesid=a.uesid "
                 "WHERE a.format IS NOT NULL "
                 "AND b.seq IN (0,1,2,3) "
                 "GROUP BY a.format, b.seq, b.pulse; ")
        cnx.cursor.execute(query)
        rows = cnx.cursor.fetchall()
        for each in rows:
            log.out.write("%s|%d|%d|%d\n" % (each[0], each[1], each[2], each[3]))
    except Exception, e:
        print 'prt_format_leadin::%s' % e


def main():
    log = ir.Logger("fmt")
    log.out.write("format|seq|pulse|count\n")
    cnx = ir.DBConnection()
    #cnx = DBConnection(host='54.254.101.29', user='kai', passwd='p33lz3l')
    try:
        prt_format_leadin(log, cnx)
    except Exception, e:
        print 'main::%s' % e

if __name__ == '__main__':
    main()
