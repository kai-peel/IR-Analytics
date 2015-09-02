#!/usr/bin/python
__author__ = 'kai'
__version__ = '1.0'
__date__ = '31-Aug-2015'
from utils import irutils as ir

SEPARATOR = 700  # gap threshold (20 ms / 35 kHz) between frames.
EMARGIN = 3  # margin of error tolerance in pulse count.
PMARGIN = 0.20  # margin of error tolerance in percentage.


def diff(frame1, frame2):
    try:
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


def if_partial_repeat(frames):
    try:
        frame1 = frames[1]
        for i in xrange(2, len(frames)):
            if not diff(frame1, frames[i]):
                return False
        return True

    except Exception, e:
        print e


def if_full_repeat(frames):
    try:
        return diff(frames[0], frames[1])

    except Exception, e:
        print e


def segmentation(array):
    try:
        frames = []
        head = 0
        for i in xrange(0, len(array), 2):
            if array[i+1] >= SEPARATOR:
                frames.append(array[head:i+2])
                head = i + 2
        return frames

    except Exception, e:
        print e


def pulses_from_uesid(log, cnx, codesetid, uesid):
    try:
        query = ("SELECT pulse FROM uespulses WHERE uesid=%d AND frame='M' ORDER BY seq;"
                 % uesid)
        cnx.cursor.execute(query)
        results = cnx.cursor.fetchall()
        pulses = []
        for row in results:
            pulses.append(row[0])

        frames = segmentation(pulses)
        log.out.write('%d|%d|' % (len(pulses), len(frames)))  # frames count
        print("checking %d-%d[%d]: %d frames." % (codesetid, uesid, len(pulses), len(frames)))

        if len(frames) < 2:
            log.out.write('False|False\n')
            return  # single frame

        is_partial_repeat = '-'
        if len(frames) > 2:
            is_partial_repeat = if_partial_repeat(frames)
        is_full_repeat = if_full_repeat(frames)

        log.out.write('%s|%s\n' % (is_partial_repeat, is_full_repeat))

    except Exception, e:
        print e


def main():
    log = ir.Logger("mrr")
    log.out.write('CodesetID|UESID|Array Size|Frame Count|Partial Repeat|Full Repeat\n')
    cnx = ir.DBConnection()
    try:
        query = ("SELECT DISTINCT a.uesid, b.codesetid FROM uespulses a, uesidfunctionmap b, codesets c "
                 "WHERE a.uesid=b.uesid AND b.codesetid=c.codesetid "
                 "AND b.activeflag='Y' and c.activeflag='Y' "
                 "AND a.seq=300 and a.frame='M' ; ")
        cnx.cursor.execute(query)
        results = cnx.cursor.fetchall()
        for row in results:
            log.out.write("%d|%d|" % (row[1], row[0]))
            pulses_from_uesid(log, cnx, row[1], row[0])

    except Exception, e:
        print e

if __name__ == '__main__':
    main()
