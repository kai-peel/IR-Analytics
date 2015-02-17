#!/usr/bin/python
__author__ = 'kai'
__version__ = '1.0'
__date__ = '16-Feb-2015'

import sys
import os
from utils import irutils

#FILE_EXTENSION = '.pir'
FILE_EXTENSION = '.txt'

functions = {'tv': [], 'stb': [], 'dvd': [], 'av': [], 'prj': [], 'ac': []}


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


def parse_codeset(cnx, fname, dtype, brand):
    funcs = get_func_by_type(cnx, dtype)
    with open(fname, 'r') as f:
        content = f.readlines()
        for each in content:
            c = each.split('|')
            freq = int(c[1])
            func = c[3].lower()
            pulse = c[4]
            if func in funcs:
                (fmt, val) = fingerprint(freq, pulse)
    f.close()


def get_meta(filename):
    meta = filename.split()
    dtype = meta[0]
    brand = meta[2]
    return dtype, brand


def quarantine(path):
    log = irutils.Logger('qt')
    cnx = irutils.DBConnection(host="54.254.101.29")
    try:
        for f in os.listdir(path):
            if f.endswith(FILE_EXTENSION):
                (t, b) = get_meta(os.path.splitext(f)[0])
                log.write('checking \"%s\" (type=%s, brand=%s)...' % (f, t, b))
                parse_codeset(cnx, os.path.join(path, f), t.lower(), b.lower())
    except Exception, e:
        print 'quarantine:%s' % e

if __name__ == '__main__':
    try:
        inputdir = sys.argv[1:]
        quarantine(inputdir[0])
    except Exception, x:
        print 'usage: python quarantine.py input_dir'
        print '    input_dir - directory for input files.\n'
        print x