#!/usr/bin/python
__author__ = 'kai'
__version__ = '1.0'
__date__ = '5-Mar-2015'

import sys
import os
import re
from utils import irutils

DATAFILE_ID = 'IrData'
METAFILE_ID = 'IrMeta'

INNOTECH_PREFIX = 1000000

device_type_id = {'tv': 1, 'tv dvd': 1,
                  'stb': 2, 'iptv': 2, 'iptv stb': 2, 'iptv dvr': 2, 'dvr': 2, 'cbl': 2, 'sat': 2, 'sat pvr': 2,
                  'pvr+cbl': 2, 'pvr': 2, 'cbl dvr': 2, 'edvb': 2, 'media server': 2, 'pc media server': 2,
                  'stb sat': 2, 'stb+dvr': 2,
                  'dvd': 3, 'video processor': 3,
                  'bd': 4, 'bd dvd': 4, 'blu-ray': 4, 'blu-ray dvd': 4, 'dvd+blu-ray': 4,
                  'av': 5, 'avr': 5, 'aud': 5, 'audio': 5, 'soundbar': 5, 'aud cd': 5, 'aud+switch': 5, 'cd+aud': 5,
                  'ht': 5,
                  'smp': 6, 'media player': 6, 'iptv mp': 6, 'pc tv': 6,
                  'prj': 10, 'proj': 10,
                  'aud bluray': 14,
                  'dvi switch': 15, 'hdmi switch': 15, 'matrix switch': 15, 'home': 15, 'home+camera': 15,
                  'home+light': 16,
                  'ac': 18,
                  'cd': 19, 'ld': 19, 'tuner': 19,
                  'vcr': 21
                  }


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


def assign_codesetid(cnx, devices, brand, codesetid):
    brandid = -1
    try:
        dlist = devices.split(',')
        for each in dlist:
            device = each.strip()
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
        content = f.readlines()
        for each in content:
            try:
                fields = each.split('|')
                codeset = int(fields[1]) + INNOTECH_PREFIX
                device = fields[2].lower()
                if len(fields[5]) > 0:
                    brandlist = fields[5]
                elif len(fields[4]) > 0:
                    brandlist = fields[4]
                elif len(fields[3]) > 0:
                    brandlist = fields[3]
                else:
                    continue
                brands = brandlist.split(',')
                #print codeset, device, brands
                for each in brands:
                    brand = each.strip()
                    print codeset, device, brand
                    (codesetid, brandid) = assign_codesetid(cnx, device, brand, codeset)
                    if codesetid != 0:
                        log.write('|%d|%d|%d\n' % (device_type_id[device], brandid, codesetid))
            except Exception, e:
                log.write('\nproc_meta:readlines: %s\n' % e)
        f.close()
        log.log.flush()


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
    log = irutils.Logger('int')
    cnx = irutils.DBConnection()
    log.write('Filename|Type|Brand|Codeset\n')
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