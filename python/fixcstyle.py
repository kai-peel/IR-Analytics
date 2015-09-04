#!/usr/bin/python
__author__ = 'kai'
__version__ = '1.0'
__date__ = '31-Aug-2015'
from utils import irutils as ir

SEPARATOR = 0.020  # gap threshold (in sec) between frames.
EMARGIN = 3  # margin of error tolerance in pulse count.
PMARGIN = 0.20  # margin of error tolerance in percentage.


def diff(log, frame1, frame2, exact=True):
    try:
        log.out.write("%d," % (len(frame1) - len(frame2)))
        if exact and len(frame1) != len(frame2):
            return False
        # ignore the size difference, for now.
        length = min(len(frame1), len(frame2))
        for i in xrange(length-1):
            if abs(frame1[i] - frame2[i]) > EMARGIN:
                return False
            elif abs(float(frame1[i] - frame2[i]) / float(max(frame1[i], frame2[i]))) > PMARGIN:
                return False
        return True

    except Exception, e:
        print e


def if_partial_repeat(log, frames):
    try:
        frame1 = frames[1]
        for i in xrange(2, len(frames)):
            if not diff(log, frame1, frames[i]):
                return False
        return True

    except Exception, e:
        print e


def if_full_repeat(log, frames):
    try:
        return diff(log, frames[0], frames[1])
    except Exception, e:
        print e


def segmentation(array, freq):
    try:
        frames = []
        head = 0
        spacer = min(SEPARATOR * freq, 1000)
        length = (len(array) / 2) * 2  # safeguard for odd size array.
        for i in xrange(0, length, 2):
            if array[i+1] >= spacer:
                frames.append(array[head:i+2])
                head = i + 2
        return frames

    except Exception, e:
        print "exp:segmentation:%s" % e


def pulses_from_uesid(log, cnx, codesetid, uesid, freq):
    try:
        query = ("SELECT pulse FROM uespulses WHERE uesid=%d AND frame='M' ORDER BY seq;"
                 % uesid)
        cnx.cursor.execute(query)
        results = cnx.cursor.fetchall()
        pulses = []
        for row in results:
            pulses.append(row[0])

        frames = segmentation(pulses, freq)
        log.out.write('%d|%d|' % (len(pulses), len(frames)))  # frames count
        print("checking set:%d id:%d[%d] (freq=%d): %d frames." % (codesetid, uesid, len(pulses), freq, len(frames)))

        if len(frames) < 2:
            log.out.write('|False||False\n')
            return  # single frame

        is_partial_repeat = '-'
        if len(frames) > 2:
            is_partial_repeat = if_partial_repeat(log, frames)
        log.out.write("|%s|" % is_partial_repeat)

        is_full_repeat = if_full_repeat(log, frames)
        log.out.write("|%s\n" % is_full_repeat)

        if is_full_repeat:

    except Exception, e:
        print e


def main():
    log = ir.Logger("mrr")
    log.out.write('CodesetID|UESID|Freqency|Array Size|Frame Count|Partial Repeat|Full Repeat\n')
    #cnx = ir.DBConnection()
    cnx = ir.DBConnection(host='54.254.101.29', user='kai', passwd='p33lz3l')
    try:
        query = ("SELECT a.uesid, b.codesetid, d.frequency FROM uespulses a "
                 "JOIN uesidfunctionmap b ON a.uesid=b.uesid "
                 "JOIN codesets c ON b.codesetid=c.codesetid "
                 "JOIN uescodes d ON b.uesid=d.uesid "
                 "WHERE a.seq>500 and a.frame='M' "
                 "AND b.activeflag='Y' and c.activeflag='Y'"
                 "GROUP BY a.uesid; ")
        cnx.cursor.execute(query)
        results = cnx.cursor.fetchall()
        for row in results:
            log.out.write("%d|%d|%d|" % (row[1], row[0], row[2]))
            pulses_from_uesid(log, cnx, row[1], row[0], row[2])
            log.out.flush()

    except Exception, e:
        print e


def test():
    log = ir.Logger("mrr")
    log.out.write('CodesetID|UESID|Freqency|Array Size|Frame Count|Partial Repeat|Full Repeat\n')
    #cnx = ir.DBConnection()
    cnx = ir.DBConnection(host='54.254.101.29', user='kai', passwd='p33lz3l')
    #log.out.write("%d|%d|%d|" % (691005, 473096, 38000))
    #pulses_from_uesid(log, cnx, 691005, 473096, 38000)
    log.out.write("%d|%d|%d|" % (1004194, 181972, 36000))
    pulses_from_uesid(log, cnx, 1004194, 181972, 36000)


if __name__ == '__main__':
    #main()
    test()
