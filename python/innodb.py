#!/usr/bin/python
__author__ = 'kai'
__version__ = '1.0'
__date__ = '16-Apr-2015'

import sys
import os
import re
from utils import irutils

DATAFILE_ID = 'IrData'
METAFILE_ID = 'Meta'

INNOTECH_PREFIX = 1000000

device_type_id = {'tv': 1, 'stb': 2, 'dvd': 3, 'av': 5, 'audio': 5, 'smp': 6, 'iptv mp': 6, 'prj': 10, 'ac': 18, 'vcr': 21}


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


def assign_codesetid(cnx, device, brand, codesetid):
    try:
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


def proc_meta(log, cnx, filename):
    with open(filename, 'r') as f:
        rnum = 0
        rdate = ''
        content = f.readlines()
        for each in content:
            try:
                fields = each.split('|')
                if fields[0].lower().find('release') > -1:
                    #rel = re.split(' \t\n', fields[0])
                    rel = re.split(r'[;, \t\s]\s*', fields[0])
                    #rel = fields[0].split(' ')
                    rnum = int(rel[1])
                    rdate = rel[2].strip()
                elif fields[1].isdigit():
                    log.out.write('%s|%d|%s\n' % (each.rstrip(), rnum, rdate))
            except Exception, e:
                log.write('\nproc_meta:readlines: %s\n' % e)
        f.close()
        log.out.flush()


def proc_data(log, filename):
    with open(filename, 'r') as f:
        content = f.readlines()
        for each in content:
            try:
                if len(each) > 24:
                    fields = each.split('|')
                    cid = int(fields[2]) + INNOTECH_PREFIX
                    freq = fields[3]
                    style = fields[4]
                    func = fields[6]
                    mframe = fields[8].rstrip()
                    rframe = fields[9].rstrip()
                    log.out.write('%d|%s|%s|%s|%s|%s|\n' % (cid, freq, style, func, mframe, rframe))
            except Exception, e:
                log.write('\nproc_data:readlines:%s\n' % e)
        f.close()
        log.out.flush()


def innotech(path):
    log = irutils.Logger('md')
    cnx = irutils.DBConnection()
    log.out.write('Encoded category|Codeset|Category by name|Region|Provider|Brand|Remote|Model|Descriptor|Release|Date\n')
    try:
        for f in os.listdir(path):
            print f
            if f.lower().find(DATAFILE_ID.lower()) > -1:
                proc_data(log, os.path.join(path, f))
            elif f.lower().find(METAFILE_ID.lower()) > -1:
                proc_meta(log, cnx, os.path.join(path, f))

    except Exception, e:
        log.write('\ninnotech:%s\n' % e)

if __name__ == '__main__':
    try:
        input_dir = sys.argv[1:]
        innotech(input_dir[0])
    except Exception, x:
        print 'usage: python innotech.py input_dir'
        print '    input_dir - directory for input files.\n'
        print x