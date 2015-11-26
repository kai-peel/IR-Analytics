#!/usr/bin/python
__author__ = 'kai'
__version__ = '0.3'
__date__ = '2015-10-28'
from utils import irutils as ir
import codecs
import numpy as np
import math
import time
import datetime
#import pickle
FREQUENCY_TOLERANCE_RANGE = 1000
BURST_MAX_STEP = 5  # pulse counts.
BURST_MIN_STEP = 1  # pulse counts.
SEPARATION_SIZE = 20  # frame mark at 20 msec from global cache.
GAP_SIZE = 10  # checksum mark at 10 msec.
USE_USEC = True  # switch between microsecond calculation (frequency independent) and pulse count.
BIN_MAX = 31  # (2 * maximum encoding value) -1.


def median(a):
    try:
        a.sort()
        # use median with a fixed error threshold.
        h = int(math.floor(len(a) / 2.0))
        return a[h]

    except Exception, e:
        print 'median::%s' % e


def average(a):
    try:
        # "InterQuartile Range Rule" for outlier detection.
        if len(a) > 3:
            qtr = int(math.floor(len(a) / 4.0))
            # ascending array
            a.sort()
            q1 = a[qtr] - 1.5 * (a[-qtr-1] - a[qtr])
            q3 = a[-qtr-1] + 1.5 * (a[-qtr-1] - a[qtr])
            # excluding outliers.
            m = []
            for ea in a:
                if q1 <= ea <= q3:
                    m.append(ea)
            avg = np.nanmean(m)
            return avg

        avg = np.nanmean(a)
        return avg

    except Exception, e:
        print 'average::%s' % e


def average2(a):
    try:
        m = average(a)
        if math.isnan(m):
            return median(a)
        return m
    except Exception, e:
        print 'average2::%s' % e


def analyze(a, freq):
    if USE_USEC:
        rmax = (BURST_MAX_STEP * 1000000.0) / freq
        rmin = (BURST_MIN_STEP * 1000000.0) / freq
    else:
        rmax = BURST_MAX_STEP
        rmin = BURST_MIN_STEP
    try:
        a.sort()
        # check if more than one value.
        if (a[-1] - a[0]) <= rmax:
            return [average(a)]

        b = int(math.ceil((a[-1] - a[0]) / rmin))
        h = np.histogram(a, bins=b)
        val = 0
        peak = 0
        bins = []
        odd = 1  # int(len(a) / 100.0)  # exclude value in small quantity (< 1%).
        for x in xrange(len(h[0])):
            if h[0][x] <= odd:
                # reset at space.
                if val > 0:
                    bins.append((h[1][peak] + h[1][peak + 1]) / 2)
                    val = 0
            elif h[0][x] > val:
                # record heavier bin
                peak = x
                val = h[0][x]
        # add the tail.
        if val > 0:
            bins.append((h[1][peak] + h[1][peak + 1]) / 2)
        return bins

    except Exception, e:
        print 'analyze::%s' % e


def analyze_hex(a):
    try:
        a.sort()
        bins = []
        hist = [[None]] * 16
        step = (a[-1] - a[0]) / 16.0
        for ea in a:
            idx = int(math.floor((ea - a[0]) / step))
            hist[idx].append(ea)
        for ea in hist:
            bins.append(average(ea))
        return bins

    except Exception, e:
        print 'analyze_hex::%s' % e


def analyze2(a, freq):
    try:
        bins = analyze(a, freq)
        if len(bins) > 16:
            bins = analyze_hex(a)
        return bins

    except Exception, e:
        print 'analyze2::%s' % e


class _IRProtocol:
    def __init__(self, name, frequency):
        self.id = 999999  # protocol's unique id
        self.name = name  # protocol's name
        self.frequency = frequency  # carrier frequency
        self.rcnt = 1  # repeat count.
        self.linH = 0  # lead-in burst pair.
        self.linL = 0  # lead-in burst pair.
        self.loutH = 0  # lead-out burst pair.
        self.loutL = 0  # lead-out burst pair.
        self.rinH = 0  # lead-in burst pair for repeat frame.
        self.rinL = 0  # lead-in burst pair for repeat frame.
        self.routH = 0  # lead-out burst pair for repeat frame.
        self.routL = 0  # lead-out burst pair for repeat frame.
        self.gapL = 0  # maker for checksum.
        self.lsb = True  # least significant bit first.
        self.dtlen = 0  # length/size of data in bit
        self.dta = []  # burst pair array. one pair per encoding value.
        self.gapL = 0

        self.t_linH = 0  # lead-in burst pair.
        self.t_linL = 0  # lead-in burst pair.
        self.t_loutH = 0  # lead-out burst pair.
        self.t_loutL = 0  # lead-out burst pair.
        self.t_rinH = 0  # lead-in burst pair for repeat frame.
        self.t_rinL = 0  # lead-in burst pair for repeat frame.
        self.t_routH = 0  # lead-out burst pair for repeat frame.
        self.t_routL = 0  # lead-out burst pair for repeat frame.
        self.t_gapL = 0  # maker for checksum.
        self.t_dta = []  # burst pair array. one pair per encoding value.

        # raw intermediate data
        self._leadinH = []
        self._leadinL = []
        self._leadoutH = []
        self._leadoutL = []
        self._repinH = []
        self._repinL = []
        self._repoutH = []
        self._repoutL = []
        self._datalen = []
        self._dataH = []
        self._dataL = []
        self._gapL = []
        self._repCnt = []

    def calc(self):
        try:
            self.dtlen = median(self._datalen)
            self.rcnt = median(self._repCnt)

            if len(self._leadinH) > 0:
                self.t_linH = median(self._leadinH)
                self.t_linL = median(self._leadinL)
                self.linH = usec2pulse(self.t_linH, self.frequency)
                self.linL = usec2pulse(self.t_linL, self.frequency)
            if len(self._leadoutH) > 0:
                self.t_loutH = median(self._leadoutH)
                self.t_loutL = median(self._leadoutL)
                self.loutH = usec2pulse(self.t_loutH, self.frequency)
                self.loutL = usec2pulse(self.t_loutL, self.frequency)
            if len(self._repinH) > 0:
                self.t_rinH = median(self._repinH)
                self.t_rinL = median(self._repinL)
                self.rinH = usec2pulse(self.t_rinH, self.frequency)
                self.rinL = usec2pulse(self.t_rinL, self.frequency)
            if len(self._repoutH) > 0:
                self.t_routH = median(self._repoutH)
                self.t_routL = median(self._repoutL)
                self.routH = usec2pulse(self.t_routH, self.frequency)
                self.routL = usec2pulse(self.t_routL, self.frequency)
            if len(self._gapL) > 0:
                self.t_gapL = median(self._gapL)
                self.gapL = usec2pulse(self.t_gapL, self.frequency)

            # data decoding logic.
            dH = analyze2(self._dataH, self.frequency)
            dL = analyze2(self._dataL, self.frequency)

            # pulse modulation encoders.
            for pH in dH:
                for pL in dL:
                    self.t_dta.append([pH, pL])
                    self.dta.append([usec2pulse(pH, self.frequency), usec2pulse(pL, self.frequency)])
        except Exception, e:
            print 'calc::%s' % e


class _Logger:
    start_time = None

    def __init__(self, tag):
        time_stamp_suffix = time.strftime("%y%m%d%H%M")
        protocol_filename = "%s%s_protocol.csv" % (tag, time_stamp_suffix)
        usec_filename = "%s%s_usec.csv" % (tag, time_stamp_suffix)
        codeset_filename = "%s%s_codesets.csv" % (tag, time_stamp_suffix)
        code_filename = "%s%s_keycodes.csv" % (tag, time_stamp_suffix)
        self.prot = codecs.open(protocol_filename, 'w', 'utf-8')
        self.usec = codecs.open(usec_filename, 'w', 'utf-8')
        self.cset = codecs.open(codeset_filename, 'w', 'utf-8')
        self.keys = codecs.open(code_filename, 'w', 'utf-8')
        self.start_time = datetime.datetime.now()
        print "Started: %s.\n" % self.start_time

    def __del__(self):
        end_time = datetime.datetime.now()
        print "Duration: from %s to %s (%s).\n" % (self.start_time, end_time, (end_time - self.start_time))
        self.prot.close()
        self.usec.close()
        self.cset.close()
        self.keys.close()


def pulse2usec(pulse, frequency):
    try:
        if USE_USEC:
            return (pulse * 1000000.0) / float(frequency)
        else:
            return pulse
    except Exception, e:
        print 'pulse2usec::%s' % e


def usec2pulse(usec, frequency):
    try:
        if USE_USEC:
            return int(round((usec * float(frequency)) / 1000000.0))
        else:
            return usec
    except Exception, e:
        print 'usec2pulse::%s' % e


def pparray2msarray(pulses, frequency):
    try:
        a = []
        for ea in pulses:
            a.append((ea * 1000000.0) / float(frequency))
        return a

    except Exception, e:
        print 'pparray2msarray::%s' % e


def add_to_data(prot, freq, pulses):
    try:
        th = int((SEPARATION_SIZE * freq) / 1000.0)
        gp = int((GAP_SIZE * freq) / 1000.0)
        for x in xrange(1, len(pulses), 2):
            prot._dataH.append(pulse2usec(pulses[x-1], freq))
            # check on gap.
            if pulses[x] >= th:
                prot._leadoutL.append(pulse2usec(pulses[x], freq))
                prot._datalen.append(x-1)
                return
            elif pulses[x] >= gp:
                prot._gapL.append(pulse2usec(pulses[x], freq))
            else:
                prot._dataL.append(pulse2usec(pulses[x], freq))
        prot._datalen.append(len(pulses))

    except Exception, e:
        print 'add_to_data::%s' % e


def add_to_main_data(prot, freq, pulses):
    try:
        if len(pulses) < 4:
            return
        prot._leadinH.append(pulse2usec(pulses[0], freq))
        prot._leadinL.append(pulse2usec(pulses[1], freq))
        prot._leadoutH.append(pulse2usec(pulses[-2], freq))
        prot._leadoutL.append(pulse2usec(pulses[-1], freq))
        if len(pulses) > 4:
            add_to_data(prot, freq, pulses[2:-2])
    except Exception, e:
        print 'add_to_main_data::%s' % e


def add_to_repeat_data(prot, freq, pulses):
    try:
        if len(pulses) < 4:
            return
        prot._repinH.append(pulse2usec(pulses[0], freq))
        prot._repinL.append(pulse2usec(pulses[1], freq))
        prot._repoutH.append(pulse2usec(pulses[-2], freq))
        prot._repoutL.append(pulse2usec(pulses[-1], freq))
        if len(pulses) > 4:
            add_to_data(prot, freq, pulses[2:-2])
    except Exception, e:
        print 'add_to_repeat_data::%s' % e


def get_pulse_pairs(prot, uesid):
    try:
        r = ir.get_ir_pulses(uesid)
        freq = int(r['frequency'])
        prot._repCnt.append(int(r['repeatcount']))

        if len(r['mainframe']):
            add_to_main_data(prot, freq, map(int, r['mainframe'].split(' ')))

        if len(r['repeatframe']):
            add_to_repeat_data(prot, freq, map(int, r['repeatframe'].split(' ')))

        if len(r['toggleframe1']):
            add_to_main_data(prot, freq, map(int, r['toggleframe1'].split(' ')))

        if len(r['toggleframe2']):
            add_to_main_data(prot, freq, map(int, r['toggleframe2'].split(' ')))

    except Exception, e:
        print 'get_pulse_pairs::%s' % e


def get_pulse_pairs_from_keys(prot, keys):
    try:
        a = map(int, keys.split(','))
        for ea in a:
            get_pulse_pairs(prot, int(ea))

    except Exception, e:
        print 'get_pulse_pairs_from_keys::%s' % e


def get_elements(cnx, frequency, keys, index):
    try:
        sql = ("SELECT a.pulse, b.frequency FROM uespulses a "
               "JOIN uescodes b ON b.uesid = a.uesid "
               "WHERE a.uesid IN (%s) "
               "AND a.seq = '%d' "
               "ORDER BY a.pulse; "
               % (keys, index))
        cnx.cursor.execute(sql)
        r = cnx.cursor.fetchall()

        a = []
        # "InterQuartile Range Rule" for outlier detection.
        if len(r) > 3:
            qtr = int(math.floor(len(r) / 4.0))
            # ascending array
            q1 = r[qtr][0] - 1.5 * (r[-qtr-1][0] - r[qtr][0])
            q3 = r[-qtr-1][0] + 1.5 * (r[-qtr-1][0] - r[qtr][0])
            for ea in r:
                if q1 <= ea[0] <= q3:
                    a.append(ea[0] * 1000000.0 / ea[1])
        else:
            for ea in r:
                a.append(ea[0] * 1000000.0 / ea[1])

        t = np.mean(a)
        c = (t * frequency) / 1000000.0
        return round(c), round(t)

    except Exception, e:
        print 'get_elements::%s' % e


##
# use median with a fixed error threshold.
#
def chk_frequencies(cnx, keys):
    try:
        sql = ("SELECT a.frequency, a.uesid FROM uescodes a "
               "WHERE a.uesid IN (%s) "
               "GROUP BY a.uesid "
               "ORDER BY a.frequency; "
               % keys)
        cnx.cursor.execute(sql)
        r = cnx.cursor.fetchall()

        # use median with a fixed error threshold.
        h = int(math.floor(len(r) / 2.0))
        frequency = r[h][0]
        k = ""
        for ea in r:
            if abs(ea[0] - frequency) < FREQUENCY_TOLERANCE_RANGE:
                k += ("%s," % str(ea[1]))
        k = k[:-1]
        return frequency, k

    except Exception, e:
        print 'chk_frequencies::%s' % e


##
# only return keys with the same ir protocol format.
#
def get_keys(log, cnx, codesetid):
    try:
        sql = ("SELECT a.format FROM uescodes a "
               "JOIN uesidfunctionmap b ON b.uesid = a.uesid "
               "WHERE b.activeflag = 'Y' "
               "AND b.codesetid = %d "
               "AND a.format IS NOT NULL AND a.format <> '' "
               "GROUP BY a.format "
               "ORDER BY count(*) DESC; "
               % codesetid)
        cnx.cursor.execute(sql)
        r = cnx.cursor.fetchall()

        # only keys of the same ir protocol format.
        if len(r) > 0:
            fmt = r[0][0]
            sql = ("SELECT a.uesid, a.functionid, b.encodedbinary2 FROM uesidfunctionmap a "
                   "JOIN uescodes b ON b.uesid = a.uesid "
                   "WHERE a.activeflag = 'Y' "
                   "AND a.codesetid = %d "
                   "AND b.format = '%s' "
                   "GROUP BY a.uesid; "
                   % (codesetid, fmt))
            cnx.cursor.execute(sql)
            r = cnx.cursor.fetchall()
            keys = ""
            for ea in r:
                keys += ("%s," % str(ea[0]))
                log.write("%d|%d|%d|%s\n" % (ea[0], codesetid, ea[1], ea[2]))
            keys = keys[:-1]
            return fmt, keys

    except Exception, e:
        print 'get_keys::%s' % e


def get_codesets(cnx, fmt):
    try:
        sql = ("SELECT a.codesetid FROM codesets a "
               "JOIN uesidfunctionmap b ON b.codesetid = a.codesetid "
               "JOIN uescodes c ON c.uesid = b.uesid "
               "WHERE a.activeflag = 'Y' AND b.activeflag = 'Y' "
               "AND b.functionid IN (23, 332, 15, 13, 18, 34, 154) "
               "AND c.format = '%s' "
               "GROUP BY a.codesetid; " % fmt)
        cnx.cursor.execute(sql)
        return cnx.cursor.fetchall()

    except Exception, e:
        print "get_codesets::%s" % e


def protocol_print(logs, prot):
    try:
        #logs.cset.write("codeset_id|protocol_id|repeat_count|data_length\n")
        logs.cset.write("%d|%d\n" % (prot.rcnt, prot.dtlen))
        logs.cset.flush()

        #logs.prot.write("protocol_id|format|frequency|little_endian|lead_in|lead_out|repeat_in|repeat_out|encoders\n")
        logs.prot.write("%r|%d,%d|%d,%d|%d,%d|%d,%d|%s\n" %
                        (prot.lsb,
                         prot.linH, prot.linL,
                         prot.loutH, prot.loutL,
                         prot.rinH, prot.rinL,
                         prot.routH, prot.routL,
                         prot.dta))
        logs.prot.flush()

        logs.usec.write("%r|%d,%d|%d,%d|%d,%d|%d,%d|%s\n" %
                        (prot.lsb,
                         prot.t_linH, prot.t_linL,
                         prot.t_loutH, prot.t_loutL,
                         prot.t_rinH, prot.t_rinL,
                         prot.t_routH, prot.t_routL,
                         prot.t_dta))
        logs.usec.flush()

    except Exception, e:
        print 'print_protocol::%s' % e


def protocol_analysis(logs, cnx, target):
    try:
        codesets = get_codesets(cnx, target)
        for ea in codesets:
            (fmt, keys) = get_keys(logs.keys, cnx, ea[0])
            logs.keys.flush()

            (freq, keys) = chk_frequencies(cnx, keys)
            prot = _IRProtocol(fmt, freq)
            logs.prot.write("%d|%d|%s|%d|" % (prot.id, ea[0], fmt, freq))

            (content, length) = ir.get_ir_codeset2(ea[0])
            logs.cset.write("%d|%d|%d|" % (ea[0], prot.id, length))

            get_pulse_pairs_from_keys(prot, keys)
            prot.calc()
            #a.append(prot)
            protocol_print(logs, prot)

    except Exception, e:
        print 'protocol_analysis::%s' % e


def test(codeset=0):
    cnx = ir.DBConnection()
    logs = _Logger("tset")
    logs.prot.write("protocol_id|codeset_id|format|frequency|little_endian|lead_in|lead_out|repeat_in|repeat_out|encoders\n")
    logs.usec.write("protocol_id|codeset_id|format|frequency|little_endian|lead_in|lead_out|repeat_in|repeat_out|encoders\n")
    logs.cset.write("codeset_id|protocol_id|cloud_size|repeat_count|content_length\n")
    logs.keys.write("code_id|codeset_id|function_id|content\n")
    try:
        codesets = [[100012], [100038], [100040], [100043], [100054], [180081], [180135], [180136], [180138], [180139], [180141], [180143], [180146], [180148], [180152], [180154], [180157], [180159], [180162], [180164], [180166], [180168], [180170], [180171], [180172], [180173], [180175], [180176], [180179], [180180], [180181], [180182], [180183], [180184], [180185], [180186], [180187], [180188], [180189], [180190], [180191], [180192], [180193], [180194], [180195], [180196], [180197], [180198], [180199], [180201], [180202], [180203], [180204], [180205], [180206], [190018], [190028], [190032], [190034], [190064], [190077], [190080], [190105], [190116], [190118], [190154], [190190], [190207], [190211], [190213], [190318], [191576], [191592], [191593], [191606], [191699], [191700], [191751], [191752], [191753], [191754], [191755], [191757], [191761], [191772], [191783], [191789], [191866], [192753], [192914], [192944], [200012], [200063], [280060], [280061], [280111], [280112], [280113], [280114], [280118], [280119], [280122], [280124], [280125], [280126], [280127], [280128], [280131], [280132], [280133], [280137], [280138], [280141], [280143], [280144], [280145], [280147], [280148], [280149], [280151], [280152], [280153], [280155], [280156], [280157], [280162], [280165], [280167], [280169], [280170], [280173], [280175], [280177], [280178], [280181], [280183], [280184], [280186], [280187], [290024], [290133], [290134], [290394], [290507], [290798], [1000001], [1000510], [1000592], [1000607], [1000646], [1000680], [1000688], [1000698], [1000703], [1000704], [1000708], [1000709], [1000812], [1000856], [1000928], [1000930], [1000944], [1000963], [1000970], [1000971], [1000975], [1000988], [1000993], [1000996], [1001206], [1001395], [1001401], [1001648], [1001840], [1001917], [1001922], [1001926], [1001959], [1002412], [1002471], [1002492], [1003006], [1003031], [1003040], [1003082], [1003261], [1004057], [1004103], [1004109], [1004116], [1004217], [1004218], [1004220], [1004226], [1004227], [1004231], [1004243], [1004263], [1004298], [1004299], [1004300], [1004306], [1004625], [1004669], [1004752], [1004806], [1005065], [11004343], [11004344], [11004364], [11004365], [11004424], [11004425], [11004426], [11004427], [11004428], [11004814], [11004816]]
        #codesets = [[codeset]]
        prot = _IRProtocol('uPD6121G', 38400)
        for ea in codesets:
            (fmt, keys) = get_keys(logs.keys, cnx, ea[0])
            logs.keys.flush()

            (freq, keys) = chk_frequencies(cnx, keys)
            freq = 38400
            prot = _IRProtocol(fmt, freq)
            logs.prot.write("%d|%d|%s|%d|" % (prot.id, ea[0], fmt, freq))

            (content, length) = ir.get_ir_codeset2(ea[0])
            logs.cset.write("%d|%d|%d|" % (ea[0], prot.id, length))

            get_pulse_pairs_from_keys(prot, keys)
            prot.calc()
            #a.append(prot)
            protocol_print(logs, prot)

    except Exception, e:
        print 'test::%s' % e


def main():
    try:
        cnx = ir.DBConnection()
        logs = _Logger("pdm")
        logs.prot.write("protocol_id|codeset_id|format|frequency|little_endian|lead_in|lead_out|repeat_in|repeat_out|encoders\n")
        logs.cset.write("codeset_id|protocol_id|cloud_size|repeat_count|content_length\n")
        logs.keys.write("code_id|codeset_id|function_id|content\n")
        #test_all(cnx, logs)
        protocol_analysis(logs, cnx, 'ECHOSTAR-D5C5(56KHz)')
    except Exception, e:
        print "main::%s" % e


def test_all(cnx, logs):
    try:
        # list out formats by popularity.
        sql = ("SELECT c.format FROM codesets a "
               "JOIN uesidfunctionmap b ON b.codesetid = a.codesetid "
               "JOIN uescodes c ON c.uesid = b.uesid "
               "WHERE a.activeflag = 'Y' AND b.activeflag = 'Y' "
               #"AND b.functionid IN (23, 332, 15, 13, 154) "
               "AND c.format IS NOT NULL AND c.format <> '' "
               "GROUP BY c.format "
               "ORDER BY count(*) DESC; ")
        cnx.cursor.execute(sql)
        rows = cnx.cursor.fetchall()
        for each in rows:
            protocol_analysis(logs, cnx, each[0])
    except Exception, e:
        print "main::%s" % e


if __name__ == '__main__':
    main()
    #test(290718)
