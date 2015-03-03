#!/usr/bin/python
__author__ = 'kai'
__version__ = '1.0'
__date__ = '2-Mar-2015'

import sys
import os
import re
from utils import irutils

FILE_EXTENSION = '.txt'
FILE_EXTENSION2 = '.TXT'

device_type_id = {'tv': 1, 'stb': 2, 'dvd': 3, 'av': 5, 'prj': 10, 'ac': 18}


def assign_codesetid(cnx, device, brand):
    try:
        codesetid = (device_type_id[device] + 1) * 100000
        if codesetid > 700000:
            codesetid = 700000

        query = ("SELECT MAX(codesetid) FROM codesets WHERE codesetid < %d "
                 % codesetid)
        cnx.cursor.execute(query)
        row = cnx.cursor.fetchone()
        codesetid = row[0] + 1

    except Exception, e:
        print 'assign_codesetid:%s' % e
        return []


def get_meta(filename):
    meta = re.split(' |  |_', filename)
    device = meta[0]
    brand = meta[2]
    return device, brand


def batch_insert(path):
    log = irutils.Logger('bi')
    cnx = irutils.DBConnection()
    log.out.write('Filename|Codeset\n')
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
        batch_insert(input_dir[0])
    except Exception, x:
        print 'usage: python batchin.py input_dir'
        print '    input_dir - directory for input files.\n'
        print x