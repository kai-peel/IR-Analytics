#!/usr/bin/python
__author__ = 'kai'
__version__ = '1.0'
__date__ = '16-Feb-2015'

import sys
import os
import time
import re
from collections import Counter
from utils import irutils
from utils import ygutils

#FILE_EXTENSION = '.pir'
FILE_EXTENSION = '.txt'
FILE_EXTENSION2 = '.TXT'

functions = {'tv': [], 'stb': [], 'dvd': [], 'av': [], 'prj': [], 'ac': []}
device_type_id = {'tv': 1, 'stb': 2, 'dvd': 3, 'av': 5, 'prj': 10, 'ac': 18}


def get_func_by_type(cnx, dtype):
    global functions
    tbl = dtype + 'functions'
    try:
        if len(functions[dtype]) == 0:
            query = ("SELECT functionname FROM %s WHERE functiongroup='Basic'" % tbl)
            cnx.cursor.execute(query)
            funcs = cnx.cursor.fetchall()
            for each in funcs:
                functions[dtype].append(each[0].lower())
        #print functions[dtype]
        return functions[dtype]
    except Exception, e:
        print 'get_func_by_type:%s' % e
        return functions[dtype]


def yg_fprint(log, freq, pulse):
    try:
        th = ygutils.Listener(freq)
        th.start()
        time.sleep(2)

        ir = str(freq) + ',' + pulse
        #log.write('send \"%s\".\n' % ir)
        irutils.testadb_rooted_s4(ir)

        th.join()
        if len(th.data_full_code) > 0:
            log.write('recv \"%s\", \"%s\".\n' % (th.data_format, th.data_full_code))
            return th.data_format, th.data_full_code
    except Exception, e:
        #log.write('yg_fprint:%s' % e)
        return None, None


def check_brand_in_codesets(cnx, brand, list):
    try:
        query = ("SELECT DISTINCT a.codesetid FROM codesets a, brands b "
                 "WHERE a.brandid=b.brandid "
                 "AND b.brandname LIKE '%s' "
                 "AND a.codesetid IN (%s) " % (brand, list))
        cnx.cursor.execute(query)
        return cnx.cursor.fetchall()
    except Exception, e:
        print 'check_brand_in_codesets:%s' % e
        return []


def check_irdb(cnx, val, func, dtype):
    try:
        query = ("SELECT DISTINCT a.codesetid FROM uesidfunctionmap a, uescodes b, codesets c, functions d "
                 "WHERE a.uesid=b.uesid AND a.codesetid=c.codesetid AND a.functionid=d.id "
                 "AND a.activeflag='Y' and c.activeflag='Y' "
                 "AND d.functionname LIKE '%s' AND b.encodedbinary2='%s' "
                 "AND c.devicetypeid=%d " % (func, val, device_type_id[dtype]))
        cnx.cursor.execute(query)
        return cnx.cursor.fetchall()
    except Exception, e:
        print 'check_irdb:%s' % e
        return []


def check_irdb_w_brand(cnx, val, func, dtype, brand):
    try:
        query = ("SELECT DISTINCT a.codesetid FROM uesidfunctionmap a, uescodes b, codesets c, functions d, brands e "
                 "WHERE a.uesid=b.uesid AND a.codesetid=c.codesetid AND a.functionid=d.id AND c.brandid=e.brandid "
                 "AND a.activeflag='Y' and c.activeflag='Y' "
                 "AND d.functionname LIKE '%s' AND b.encodedbinary2='%s' "
                 "AND e.brandname LIKE '%s' AND c.devicetypeid=%d " % (func, val, brand, device_type_id[dtype]))
        cnx.cursor.execute(query)
        return cnx.cursor.fetchall()
    except Exception, e:
        print 'check_irdb_w_brand:%s' % e
        return []


def check_codeset(log, cnx, fname, dtype, brand):
    old = False
    key_count = 0
    try:
        funcs = get_func_by_type(cnx, dtype)
        key_count = 0
        dups = Counter()
        with open(fname, 'r') as f:
            content = f.readlines()
            for each in content:
                try:
                    c = each.split('|')
                    freq = int(c[1])
                    func = c[3].lower()
                    pulse = c[4].rstrip()
                    if func in funcs:
                        (fmt, val) = yg_fprint(log, freq, pulse)
                        if val is not None:
                            key_count += 1
                            codesets = check_irdb(cnx, val, func, dtype)
                            print codesets
                            for codeset in codesets:
                                dups[str(codeset[0])] += 1
                except Exception, e:
                    log.write('check_codeset:readlines: %s' % e)
            log.write('Duplicate codesets: %s.\n' % dups)
            log.write('Total key checked: %d.\n' % key_count)
            sz_codesets = ''
            for each in dups:
                # key_count - 1, for we are checking both "power" and "poweron".
                if dups[each] >= (key_count - 1):
                    #log.out.write('%s,' % each)
                    sz_codesets += ('%s,' % each)
                    old = True
            if old and len(sz_codesets) > 0:
                codesets = check_brand_in_codesets(cnx, brand, sz_codesets[:-1])
                for codeset in codesets:
                    log.out.write('%d,' % codeset[0])
                log.out.write('|')
            log.out.write('%s' % sz_codesets)
            log.out.write('|%d|%s\n' % (key_count, dups))
        f.close()
        return old, key_count
    except Exception, e:
        log.write('check_codeset:%s' % e)
        return old, key_count


def get_meta(filename):
    meta = re.split(' |  |_', filename)
    dtype = meta[0]
    brand = meta[2]
    return dtype, brand


def quarantine(path):
    log = irutils.Logger('qt')
    cnx = irutils.DBConnection()
    log.out.write('Filename|Duplicate|All Brands|Key Tested|Similar\n')
    try:
        for f in os.listdir(path):
            print f
            if f.endswith(FILE_EXTENSION) or f.endswith(FILE_EXTENSION2):
                (t, b) = get_meta(os.path.splitext(f)[0])
                log.write('\nchecking \"%s\" (type=%s, brand=%s)...\n' % (f, t, b))
                log.out.write('%s|' % f)
                (old, key_count) = check_codeset(log, cnx, os.path.join(path, f), t.lower(), b.lower())
                if old:
                    log.bat.write('move \"%s\" \"%s\"\n' % (os.path.join(path, f), os.path.join(path, 'old')))
                    #os.rename(os.path.join(path, f), os.path.join(path, 'old/' + f))
                elif key_count == 0:
                    log.bat.write('move \"%s\" \"%s\"\n' % (os.path.join(path, f), os.path.join(path, 'bad')))
                else:
                    log.bat.write('move \"%s\" \"%s\"\n' % (os.path.join(path, f), os.path.join(path, 'new')))
                log.out.flush()
                log.bat.flush()
                log.log.flush()
    except Exception, e:
        log.write('quarantine:%s' % e)

if __name__ == '__main__':
    try:
        input_dir = sys.argv[1:]
        quarantine(input_dir[0])
    except Exception, x:
        print 'usage: python quarantine.py input_dir'
        print '    input_dir - directory for input files.\n'
        print x