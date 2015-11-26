#!/usr/bin/python
__author__ = 'kai'
__version__ = '1.0'
__date__ = '2015-11-04'
import datetime
#import time
from utils import irutils as ir
from utils import pulsegen as gen
from utils import ygutils as yg
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


def get_uescode_from_cloud(uesid):
    try:
        ues_data = ir.get_ir_pulses(uesid)
        cloud_frequency = int(ues_data["frequency"])
        cloud_repeat = int(ues_data["repeatcount"])
        cloud_ir_data = ues_data["mainframe"].split(" ")
        cloud_ir_rep = ues_data["repeatframe"].split(" ")
        if len(cloud_ir_data) <= 1:
            print "try first toggle frame..."
            cloud_ir_data = ues_data["toggleframe1"].split(" ")
        return cloud_frequency, cloud_ir_data, cloud_repeat, cloud_ir_rep
    except Exception, e:
        print 'get_uescode_from_cloud: %s' % e


def test_uescode(log_hex, log_pulses, hydb, enc, uesid, encodedbinary2, fmt, syscode, datacode):
    try:
        adb_thread = yg.Listener()
        adb_thread.start()

        log_hex.write('%d|%s|%s|%d|%d|' % (uesid, encodedbinary2, fmt, syscode, datacode))
        cloud_frequency, cloud_ir_data, cloud_repeat, cloud_ir_rep = get_uescode_from_cloud(uesid)
        log_pulses.write('%d|%d|%s|%d|%s|' % (uesid, cloud_frequency, ','.join(cloud_ir_data), cloud_repeat, ','.join(cloud_ir_rep)))

        frequency, repeat_count, main_frame, repeat_frame, toggle_frame = hydb.build(enc, encodedbinary2)

        #time.sleep(1)  # stabilizer
        ir.send_cir_adb2(frequency, main_frame, repeat_count, repeat_frame)
        adb_thread.join()
        #time.sleep(1)  # stabilizer

        if adb_thread.data_full_code:
            print "format:%s, sys:%d, data:%d, full:%s." % (adb_thread.data_format, adb_thread.data_sys_code, adb_thread.data_data_code, adb_thread.data_full_code)
            log_hex.write('%d|%d|%s|%s|\n' % (adb_thread.data_sys_code, adb_thread.data_data_code, adb_thread.data_format, adb_thread.data_full_code))
            log_pulses.write('%d|%s|\n' % (adb_thread.data_wave_freq, adb_thread.data_wave_buf))
        else:
            log_hex.write('||||\n')
            log_pulses.write('||\n')
        log_hex.flush()
        log_pulses.flush()
    except Exception, e:
        print 'test_format: %s' % e


def test_format(log_hex, log_pulses, irdb, hydb, fmt):
    try:
        enc = hydb.encoder(fmt)
        sql = ('SELECT a.uesid, a.encodedbinary2, a.format, a.syscode, a.datacode FROM uescodes a '
               '  JOIN uesidfunctionmap b ON b.uesid=a.uesid AND b.activeflag="Y" '
               '  JOIN codesets c ON c.codesetid=b.codesetid AND c.activeflag="Y" '
               '  WHERE a.format ="%s" GROUP BY a.uesid; ' % fmt)
        irdb.cursor.execute(sql)
        rows = irdb.cursor.fetchall()
        for ea in rows:
            uesid = ea[0]
            full_code = ea[1]
            dbfmt = ea[2]
            syscode = ea[3]
            datacode = ea[4]
            test_uescode(log_hex, log_pulses, hydb, enc, uesid, full_code, dbfmt, syscode, datacode)

    except Exception, e:
        print 'test_format: %s' % e


def get_formats(db):
    try:
        sql = 'SELECT * FROM protocols WHERE version IS NOT NULL; '
        db.cursor.execute(sql)
        rows = db.cursor.fetchall()
        return rows

    except Exception, e:
        print 'get_formats: %s' % e


def test():
    try:
        f = ir.Logger('hyg', 2)
        f.logs[0].write('uesid|db_encodedbinary2|db_fmt|db_syscode|db_datacode|')
        f.logs[0].write('data_sys_code|data_data_code|data_format|data_full_code|\n')
        f.logs[1].write('uesid|cloud_frequency|cloud_ir_data|cloud_repeat|cloud_ir_rep')
        f.logs[1].write('data_wave_freq|data_wave_buf|\n')

        #v2 = ir.DBConnection()
        v2 = ir.DBConnection(host='54.254.101.29', user='kai', passwd='p33lz3l')
        #hy = gen.Hydra(host='127.0.0.1')
        hy = gen.Hydra(host='54.254.101.29', user='kai', passwd='p33lz3l')

        fmts = get_formats(hy)
        for ea in fmts:
            fmt = ea[1]
            test_format(f.logs[0], f.logs[1], v2, hy, fmt)

    except Exception, e:
        print 'test: %s' % e

if __name__ == '__main__':
    start_time = datetime.datetime.now()
    print "Started: %s." % start_time
    test()
    end_time = datetime.datetime.now()
    print "Duration: from %s to %s (%s)." % (start_time, end_time, (end_time - start_time))
