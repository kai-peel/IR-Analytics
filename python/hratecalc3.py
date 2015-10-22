#!/usr/bin/python
__author__ = 'kai'
__version__ = '1.0'
__date__ = '2015-10-08'

import sys
import time
import datetime
import codecs
import numpy as np


class _Logger:
    start_time = None

    def __init__(self, tag):
        time_stamp_suffix = time.strftime("%Y%m%d%H%M%S")
        log_filename = "%s%s.log" % (tag, time_stamp_suffix)
        self.log = codecs.open(log_filename, 'w', 'utf-8')
        self.start_time = datetime.datetime.now()
        self.log.write("Started: %s.\n" % self.start_time)

    def __del__(self):
        end_time = datetime.datetime.now()
        self.log.write("Duration: from %s to %s (%s).\n" % (self.start_time, end_time, (end_time - self.start_time)))
        self.log.close()


def calc(a):
    m = np.median(a, axis=0)
    th = m[1]
    peak = 0
    ts = 0
    a2 = []
    for ea in a:
        # count uptick only
        if ea[1] > th:
            if ea[1] > peak:
                peak = ea[1]
                ts = ea[0]
        elif peak > 0:
            a2.append([ts, peak])
            peak = 0

    d = a[-1][0] - a[0][0]
    r = (len(a2) * 60.0) / d
    print '%d beats per second, at %.2f~%.2f sec.' % (round(r), round(a[0][0], 2), round(a[-1][0], 2))

    filename = '%.2f-%.2f_%dbps.csv' % (round(a[0][0], 2), round(a[-1][0], 2), round(r))
    log = codecs.open(filename, 'w', 'utf-8')
    for ea in a2:
        log.write('%f,%f\n' % (ea[0], ea[1]))

    return a2


def proc_data(filename):
    with open(filename, 'r') as f:
        hrates = []
        #volts = []
        content = f.readlines()
        for each in content:
            try:
                fields = each.split(',')
                tstamp = float(fields[0])
                volt = float(fields[1])
                if volt > 0.5:
                    hrates.append([tstamp, volt])
                    #volts.append(volt)
                elif len(hrates) > 0:
                    # process collected heart rates.
                    peaks = calc(hrates)
                    calc(peaks)
                    hrates = []
            except Exception, e:
                print '\nproc_data:readlines:%s\n' % e
        f.close()


def proc_full_data(filename):
    with open(filename, 'r') as f:
        hrates = []
        #volts = []
        content = f.readlines()
        for each in content:
            try:
                fields = each.split(',')
                tstamp = float(fields[0])
                volt = float(fields[1])
                hrates.append([tstamp, volt])
            except Exception, e:
                print '\nproc_data:readlines:%s\n' % e

        # process collected heart rates.
        p1 = calc(hrates)
        p2 = calc(p1)
        calc(p2)
        f.close()


def heartrate(fname):
    #log = _Logger('hrate')
    proc_full_data(fname)

if __name__ == '__main__':
    try:
        #ivar = sys.argv[1:]
        #heartrate(ivar[0])
        heartrate('/Users/kai/Downloads/data.csv')

    except Exception, x:
        print 'usage: python hratecalc.py filename'
        print '    filename - name for input files.\n'
        print x
