#!/usr/bin/python
__author__ = 'kai'
__version__ = '1.0'
__date__ = '02-Sep-2015'
from utils import irutils as ir


def find_oddsize_frame_from_uesid(log, cnx, codesetid, uesid, frame):
    try:
        query = ("SELECT count(1) FROM uespulses WHERE uesid=%d AND frame='%s'; "
                 % (uesid, frame))
        cnx.cursor.execute(query)
        results = cnx.cursor.fetchall()
        for row in results:
            is_odd = row[0] > 0 and row[0] % 2 != 0
            if is_odd:
                log.out.write("%d|%d|%s|%d\n" % (codesetid, uesid, frame, row[0]))
            return is_odd

    except Exception, e:
        print e


def find_oddsize_pulses_from_uesid(log, cnx, codesetid, uesid):
    try:
        if find_oddsize_frame_from_uesid(log, cnx, codesetid, uesid, 'M'):
            return
        elif find_oddsize_frame_from_uesid(log, cnx, codesetid, uesid, 'R'):
            return
        elif find_oddsize_frame_from_uesid(log, cnx, codesetid, uesid, 'T1'):
            return
        elif find_oddsize_frame_from_uesid(log, cnx, codesetid, uesid, 'T2'):
            return

    except Exception, e:
        print e


def main():
    log = ir.Logger("odd")
    log.out.write("CodesetID|UESID|Type|Size\n")
    cnx = ir.DBConnection()
    try:
        query = ("SELECT DISTINCT a.uesid, b.codesetid FROM uesidfunctionmap a, codesets b "
                 "WHERE a.uesid=b.uesid "
                 "AND a.activeflag='Y' and b.activeflag='Y' "
                 "GROUP BY a.uesid; ")
        cnx.cursor.execute(query)
        results = cnx.cursor.fetchall()
        for row in results:
            find_oddsize_pulses_from_uesid(log, cnx, row[1], row[0])

    except Exception, e:
        print e


def test():
    log = ir.Logger("odd")
    log.out.write("CodesetID|UESID|Type|Size\n")
    cnx = ir.DBConnection()
    find_oddsize_pulses_from_uesid(log, cnx, 691005, 473096)


if __name__ == '__main__':
    #main()
    test()
