#!/usr/bin/python
__author__ = 'kai'
__version__ = '1.0'
__date__ = '2-Mar-2015'

import sys
import os
import re
from utils import irutils

FILE_EXTENSION = '.txt'

device_type_id = {'tv': 1, 'stb': 2, 'dvd': 3, 'av': 5, 'prj': 10, 'ac': 18}


def get_brandid(cnx, brand):
    try:
        query = ("SELECT brandid FROM brands WHERE brandname LIKE '%s' " % brand)
        cnx.cursor.execute(query)
        row = cnx.cursor.fetchone()
        return row[0]

    except Exception, e:
        query = ("INSERT INTO brands (brandname) VALUES ('%s') " % brand)
        cnx.cursor.execute(query)
        cnx.db.commit()
        return 0


def assign_codesetid(cnx, device, brand):
    try:
        codesetid = (device_type_id[device] + 1) * 100000
        if codesetid > 700000:
            codesetid = 700000
        query = ("SELECT MAX(codesetid) FROM codesets WHERE codesetid < %d " % codesetid)
        cnx.cursor.execute(query)
        row = cnx.cursor.fetchone()
        codesetid = row[0] + 1

        brandid = get_brandid(cnx, brand)
        if brandid <= 0:
            brandid = get_brandid(cnx, brand)

        query = ("INSERT INTO codesets VALUES (%d, %d, %d, 999, NULL, CURDATE(), 'Y') "
                 % (brandid, device_type_id[device], codesetid))
        cnx.cursor.execute(query)
        cnx.db.commit()

        return codesetid, brandid

    except Exception, e:
        print 'assign_codesetid:%s' % e
        return 0, 0


def get_meta(filename):
    try:
        meta = re.split(' |  |_', filename)
        device = meta[0].lower()
        brand = meta[1].lower()
        return device, brand
    except Exception, e:
        print('get_meta:%s' % e)
        return None, None


def concat_files(log, fname, cid):
    with open(fname, 'r') as f:
        content = f.readlines()
        for each in content:
            try:
                if len(each) > 24:
                    c = each.split('|')
                    freq = c[2]
                    func = c[1]
                    pulse = c[3].rstrip()
                    log.out.write('%d|%s|Full_Repeat|%s|%s|\n' % (cid, freq, func, pulse))
            except Exception, e:
                log.write('\nconcat_files:%s\n' % e)
        f.close()


def batch_insert(path):
    log = irutils.Logger('bi')
    cnx = irutils.DBConnection()
    log.write('Filename|Type|Brand|Codeset\n')
    try:
        for f in os.listdir(path):
            print f
            if f.lower().endswith(FILE_EXTENSION):
                (t, b) = get_meta(os.path.splitext(f)[0])
                (codesetid, brandid) = assign_codesetid(cnx, t, b)
                log.write('%s|%d|%d|%d\n' % (f, device_type_id[t], brandid, codesetid))
                concat_files(log, os.path.join(path, f), codesetid)
                log.out.flush()
                log.log.flush()
    except Exception, e:
        log.write('\nbatch_insert:%s\n' % e)

if __name__ == '__main__':
    try:
        input_dir = sys.argv[1:]
        batch_insert(input_dir[0])
    except Exception, x:
        print 'usage: python batchin.py input_dir'
        print '    input_dir - directory for input files.\n'
        print x