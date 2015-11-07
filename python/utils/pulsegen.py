#!/usr/bin/python
__author__ = 'kai'
__version__ = '1.0'
__date__ = '2015-11-06'
import MySQLdb
import numpy as np
#import datetime
#import irutils as ir
IRDBV1 = '175.41.143.31'  # production
IRDBV2 = '54.251.240.47'  # secured production
IRDBSG = '54.254.101.29'  # staging


class ProtocolSpec:
    def __init__(self, idx, modulation, frequency, endian, toggle_bits, gap_bits, repeat_count, spec):
        self.id = idx
        self.modulation = modulation
        self.frequency = frequency
        self.repeat_count = repeat_count
        self.endian = endian
        self.toggle_bits = toggle_bits
        self.gap_bits = gap_bits
        self.lead_in = []
        self.lead_out = []
        self.repeat_in = []
        self.repeat_out = []
        self.gap = []
        self.encoder = []
        """
        CREATE TABLE `pulses` (
          `prot_id` int(10) unsigned NOT NULL,
          `seq` smallint(5) unsigned DEFAULT NULL,
          `pulse` smallint(5) unsigned DEFAULT NULL,
          `eval` tinyint(4) DEFAULT NULL,
          `state` tinyint(3) unsigned DEFAULT NULL,
          KEY `prot_id` (`prot_id`),
          KEY `frame` (`eval`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
        """
        # 0~16 := data value, -1 := lead_in, -2 := lead_out,  -3 := repeat_in,  -4 := repeat_out, -5 := gap / half mark
        try:
            for ea in spec:
                data_value = ea[3]
                pulse_count = ea[2]
                pulse_state = ea[4]
                if data_value >= 0:
                    self.insert(self.encoder, data_value, pulse_count, pulse_state)
                elif data_value == -1:
                    self.lead_in.append([pulse_count, pulse_state])
                elif data_value == -2:
                    self.lead_out.append([pulse_count, pulse_state])
                elif data_value == -3:
                    self.repeat_in.append([pulse_count, pulse_state])
                elif data_value == -4:
                    self.repeat_out.append([pulse_count, pulse_state])
                elif data_value == -5:
                    self.gap.append([pulse_count, pulse_state])

        except Exception, e:
            print "ERR:ProtocolSpec:__init__: %s" % e

    @staticmethod
    def insert(encoder_array, data_value, pulse_count, pulse_state):
        try:
            encoder_array[data_value].append([pulse_count, pulse_state])
        except IndexError:
            encoder_array.insert(data_value, [])
            encoder_array[data_value].append([pulse_count, pulse_state])
        except Exception, e:
            print "ERR:ProtocolSpec:insert: %s" % e


class Hydra:
    def __init__(self, host=IRDBV2, db='hydra', user='zdbadmin', passwd='z3l4yi23'):
        try:
            self.db = MySQLdb.connect(host=host, user=user, passwd=passwd, db=db, charset='utf8', use_unicode=True)
            self.cursor = self.db.cursor()
        except Exception, e:
            print "ERR:Hydra:__init__: %s" % e

    def __del__(self):
        try:
            self.cursor.close()
            self.db.close()
        except Exception, e:
            print "ERR:Hydra:__del__: %s" % e

    def encoder(self, fmt):
        try:
            # protocol header
            sql = ("SELECT * FROM protocols WHERE format = '%s'; " % fmt)
            self.cursor.execute(sql)
            prot = self.cursor.fetchone()
            idx = prot[0]
            modulation = prot[2]
            frequency = prot[3]
            endian = prot[4]
            toggle = prot[5]
            gap = prot[6]
            repeat = prot[7]

            # protocol data
            sql = ("SELECT * FROM pulses WHERE prot_id = %d ORDER BY seq; " % idx)
            self.cursor.execute(sql)
            rows = self.cursor.fetchall()

            enc = ProtocolSpec(idx, modulation, frequency, endian, toggle, gap, repeat, rows)
            return enc

        except Exception, e:
            print "ERR:Hydra:encoder: %s" % e

    def build(self, spec, ygval):
        try:
            # ex. "1001111 10001 [79 11]"
            # ex. "20120033 01 [860F 1]"
            full_code, hex_code = ygval.split('[')
            if hex_code:
                # radix = len(set(full_code) - set('01 ')) + 2
                data = self.build_from_binary(spec, full_code)
            else:
                data = self.build_from_hex(spec, full_code)
            return self.build_frames(spec, data)

        except Exception, e:
            print "ERR:Hydra:build: %s" % e

    @staticmethod
    def data2pulses(spec, data):
        pulses = []
        leading = 0
        current = 0
        state = 0
        try:
            for ea in data:
                if ea[1] != state:
                    # check leading 0.
                    if len(pulses) < 1 and state == 0:
                        leading = current
                    else:
                        pulses.append(current)
                    # toggle pulse's high / low.
                    current = ea[0]
                    state = ea[1]
                else:
                    current += ea[0]
            # last element.
            if state == 0:
                # recycle leading 0 to trailing.
                pulses.append(current + leading)
            else:
                pulses.append(current)
                if leading > 0:
                    pulses.append(leading)
            return pulses
        except Exception, e:
            print "ERR:PulseGen:data2pulses: %s" % e

    def build_frames(self, spec, data):
        main_frame = []
        repeat_frame = []
        toggle_frame = []
        try:
            raw = []
            # construct pulse sequence for main frame.
            if len(spec.lead_in) > 0:
                raw.extend(spec.lead_in)

            # check if there's half-marker.
            if spec.gap_bits and len(spec.gap_bits) > 0:
                gap = int(spec.gap_bits)
                for x in xrange(gap):
                    raw.extend(spec.encoder[data[x]])
                raw.extend(spec.gap)
                for x in xrange(gap, len(data)):
                    raw.extend(spec.encoder[data[x]])
            else:
                for ea in data:
                    raw.extend(spec.encoder[ea])

            if len(spec.lead_out) > 0:
                raw.extend(spec.lead_out)

            main_frame = self.data2pulses(spec, raw)

            raw = []
            # construct pulse sequence for toggle frame.
            if spec.toggle_bits and len(spec.toggle_bits) > 0:
                toggle_bits = map(int, spec.toggle_bits.split(','))
                radix = len(spec.encoder)

                if len(spec.lead_in) > 0:
                    raw.extend(spec.lead_in)

                # check if there's half-marker.
                if spec.gap_bits and len(spec.gap_bits) > 0:
                    gap = int(spec.gap_bits)
                    for x in xrange(gap):
                        if x in toggle_bits:
                            t = (data[x] + (radix / 2)) % radix
                            raw.extend(spec.encoder[t])
                        else:
                            raw.extend(spec.encoder[data[x]])
                    raw.extend(spec.gap)
                    for x in xrange(gap, len(data)):
                        if x in toggle_bits:
                            t = (data[x] + (radix / 2)) % radix
                            raw.extend(spec.encoder[t])
                        else:
                            raw.extend(spec.encoder[data[x]])
                else:
                    for x in xrange(len(data)):
                        if x in toggle_bits:
                            t = (data[x] + (radix / 2)) % radix
                            raw.extend(spec.encoder[t])
                        else:
                            raw.extend(spec.encoder[data[x]])

                if len(spec.lead_out) > 0:
                    raw.extend(spec.lead_out)
                toggle_frame = self.data2pulses(spec, raw)

            return spec.frequency, spec.repeat_count, main_frame, repeat_frame, toggle_frame

        except Exception, e:
            print "ERR:PulseGen:build_frames: %s" % e

    @staticmethod
    def build_from_binary(spec, full_code):
        data = []
        try:
            words = full_code.split(' ')
            for ea in words:
                idx = len(data)
                for c in ea:
                    # big-endian, msb reading style.
                    if spec.endian == 'B':
                        data.append(int(c))
                    # little-endian, lsb reading style.
                    else:
                        data.insert(idx, int(c))
            return data
        except Exception, e:
            print "ERR:PulseGen:build_from_binary: %s" % e

    @staticmethod
    def build_from_hex(spec, full_code):
        data = []
        try:
            return data
        except Exception, e:
            print "ERR:PulseGen:build_from_hex: %s" % e
