#!/usr/bin/python
__author__ = 'kai'
__version__ = '1.0'
__date__ = '2015-11-06'
import MySQLdb
#import binascii
import numpy as np
#import datetime
#import irutils as ir
import math
IRDBV1 = '175.41.143.31'  # production
IRDBV2 = '54.251.240.47'  # secured production
IRDBSG = '54.254.101.29'  # staging


class ProtocolSpec:
    def __init__(self, idx, modulation, frequency, endian, toggle_bits, gap_bits, repeat_count, repeat_content,
                 repeat_toggle, trailer_bits, spec):
        self.id = idx
        self.modulation = modulation
        self.frequency = frequency
        self.endian = endian
        self.toggle_bits = toggle_bits
        self.gap_bits = gap_bits
        self.repeat_count = repeat_count
        self.repeat_content = repeat_content
        self.repeat_toggle_bits = repeat_toggle
        self.lead_in = []
        self.lead_out = []
        self.repeat_in = []
        self.repeat_out = []
        self.gap = []
        self.interval = []
        self.encoder = []
        self.trailer_bits = trailer_bits
        self.trailer = []
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
                elif data_value == -6:
                    self.interval.append([pulse_count, pulse_state])
                elif data_value <= -50:
                    self.insert(self.trailer, abs(data_value + 50), pulse_count, pulse_state)

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
            rdata = prot[8]
            rtoggle = prot[9]
            trailer = prot[10]

            # protocol data
            sql = ("SELECT * FROM pulses WHERE prot_id = %d ORDER BY seq; " % idx)
            self.cursor.execute(sql)
            rows = self.cursor.fetchall()

            enc = ProtocolSpec(idx, modulation, frequency, endian, toggle, gap, repeat, rdata, rtoggle, trailer, rows)
            return enc

        except Exception, e:
            print "ERR:Hydra:encoder: %s" % e

    def build(self, spec, ygval):
        try:
            # ex. "1001111 10001 [79 11]"
            # ex. "20120033 01 [860F 1]"
            full_code = ygval.split('[')
            # radix = len(set(full_code) - set('01 ')) + 2
            data = self.build_from_hex(spec, full_code[0], (len(full_code) > 1))
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
                    # check for leading 0s, wrap it around as trailing.
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

            # pulses always start with hi state, and form in pairs.
            if (len(pulses) % 2) != 0:
                pulses.append(0)
            return pulses
        except Exception, e:
            print "ERR:PulseGen:data2pulses: %s" % e

    @staticmethod
    def set_data(pulses, position, value, encoder, trailer, trailer_pos):
        try:
            if position in trailer_pos:
                pulses.extend(trailer[value])
            else:
                pulses.extend(encoder[value])
            return position + 1
        except Exception, e:
            print "ERR:PulseGen:set_data: %s" % e

    def build_frame(self, data, encoder, lead_in, lead_out, gap, toggle_bits, gap_bits, interval, trailer_bits, trailer):
        try:
            raw = []
            pos = 0

            # alternative encoder.
            if trailer_bits and len(trailer_bits) > 0:
                trailer_pos = map(int, trailer_bits.split(','))
            else:
                trailer_pos = []

            # construct pulse sequence for main frame.
            if lead_in and len(lead_in) > 0:
                raw.extend(lead_in)

            # check if there is data content.
            if data and len(data) > 0:
                radix = len(encoder)  # encoding base.
                # construct pulse sequence for toggle frame.
                if toggle_bits and len(toggle_bits) > 0:
                    toggle_pos = map(int, toggle_bits.split(','))
                else:
                    toggle_pos = []

                # check if there is a half-marker.
                if gap_bits and len(gap_bits) > 0:
                    gap_pos = int(gap_bits)  # support only 1 gap for now.
                    for x in xrange(gap_pos):
                        if x in toggle_pos:
                            t = (data[x] + (radix / 2)) % radix
                            # raw.extend(encoder[t])
                            pos = self.set_data(raw, pos, t, encoder, trailer, trailer_pos)
                        else:
                            # raw.extend(encoder[data[x]])
                            pos = self.set_data(raw, pos, data[x], encoder, trailer, trailer_pos)
                    raw.extend(gap)
                    for x in xrange(gap_pos, len(data)):
                        if x in toggle_pos:
                            t = (data[x] + (radix / 2)) % radix
                            # raw.extend(encoder[t])
                            pos = self.set_data(raw, pos, t, encoder, trailer, trailer_pos)
                        else:
                            # raw.extend(encoder[data[x]])
                            pos = self.set_data(raw, pos, data[x], encoder, trailer, trailer_pos)
                else:
                    for x in xrange(len(data)):
                        if x in toggle_pos:
                            t = (data[x] + (radix / 2)) % radix
                            # raw.extend(encoder[t])
                            pos = self.set_data(raw, pos, t, encoder, trailer, trailer_pos)
                        else:
                            # raw.extend(encoder[data[x]])
                            pos = self.set_data(raw, pos, data[x], encoder, trailer, trailer_pos)

            if lead_out and len(lead_out) > 0:
                raw.extend(lead_out)

            if interval and len(interval) > 0:
                s = np.sum(raw, axis=0)
                raw.extend([[interval[0][0] - s[0], interval[0][1]]])

            return raw

        except Exception, e:
            print "ERR:PulseGen:build_frame: %s" % e

    def build_frames(self, spec, data):
        try:
            raw = self.build_frame(data, spec.encoder, spec.lead_in, spec.lead_out, spec.gap, None, spec.gap_bits,
                                   spec.interval, spec.trailer_bits, spec.trailer)
            main_frame = self.data2pulses(spec, raw)

            if len(spec.repeat_in) > 0 or len(spec.repeat_out) > 0 or spec.repeat_content == 'Y':
                rdata = data if spec.repeat_content == 'Y' else None
                raw = self.build_frame(rdata, spec.encoder, spec.repeat_in, spec.repeat_out, spec.gap,
                                       spec.repeat_toggle_bits, spec.gap_bits, spec.interval, spec.trailer_bits, spec.trailer)
                repeat_frame = self.data2pulses(spec, raw)
            else:
                repeat_frame = []

            if spec.toggle_bits and len(spec.toggle_bits) > 0:
                raw = self.build_frame(data, spec.encoder, spec.lead_in, spec.lead_out, spec.gap, spec.toggle_bits,
                                       spec.gap_bits, spec.interval, spec.trailer_bits, spec.trailer)
                toggle_frame = self.data2pulses(spec, raw)
            else:
                toggle_frame = []
            return spec.frequency, spec.repeat_count, main_frame, repeat_frame, toggle_frame
        except Exception, e:
            print "ERR:PulseGen:build_frames: %s" % e

    @staticmethod
    def hex_to_binary(hex_string, base):
        # bin_string = '{:08b}'.format(int(hex_string, 16))
        try:
            bin_string = ''
            d = int(hex_string, 16)
            for x in xrange(int(4 * len(hex_string.strip()) / math.log(base, 2))):
                d, m = divmod(d, base)
                bin_string = str(m) + bin_string
            return bin_string
        except Exception, e:
            print 'hex_to_binary: %s' % e

    def build_from_hex(self, spec, full_code, raw):
        data = []
        try:
            frames = full_code.split('-')
            if len(frames) > 1:
                # spec.repeat_content = 'Y'
                if spec.repeat_count < 2:
                    spec.repeat_count = 2
            frame = frames[0].strip()
            words = frame.split(' ')
            radix = len(spec.encoder)
            for ea in words:
                # check if need to convert from hex to binary.
                if not raw and radix < 16:
                    val = self.hex_to_binary(ea, radix)
                else:
                    val = ea
                idx = len(data)
                for c in val:
                    # big-endian, msb reading style.
                    if spec.endian == 'B':
                        data.append(int(c, radix))
                    # little-endian, lsb reading style.
                    else:
                        data.insert(idx, int(c, radix))
            return data
        except Exception, e:
            print "ERR:PulseGen:build_from_hex: %s" % e
