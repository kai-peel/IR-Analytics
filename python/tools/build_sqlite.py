#!/usr/bin/python
import datetime
from utils import irutils as ir
from utils import pulsegen as gen
__author__ = 'kai'
__version__ = '1.0'
__date__ = '2015-11-09'

selection = [[1, '13, 24, 30, 31, 37, 39, 41, 42, 46, 50'],
             [2, '121,137,149,137,123,137,183,137,540,137,379,137,410,137,194,120,432,37,120,380,37,134,128,194,137']
             ]

queries = [
    'CREATE TABLE k_uesidfunctionmap AS '
    '  SELECT * '
    '  FROM uesidfunctionmap WHERE activeflag = "Y" AND codesetid IN (SELECT codesetid FROM k_codesets) '
    '  GROUP BY uesid, codesetid, functionid;  ',

    'CREATE TABLE k_uescodes AS '
    '  SELECT * '
    '  FROM uescodes WHERE uesid IN (SELECT DISTINCT uesid FROM k_uesidfunctionmap WHERE activeflag = "Y") '
    '  GROUP BY uesid;  ',

    'CREATE TABLE k_functions AS '
    '  SELECT * '
    '  FROM functions WHERE id IN (SELECT DISTINCT functionid FROM k_uesidfunctionmap WHERE activeflag = "Y") '
    '  GROUP BY id;  ',

    'CREATE TABLE k_devicetypes AS '
    '  SELECT devicetypeid, devicetype '
    '  FROM devicetypes WHERE devicetypeid IN (SELECT DISTINCT devicetypeid FROM k_codesets WHERE activeflag = "Y") '
    '  GROUP BY devicetypeid;  ',

    'CREATE TABLE k_uespulses AS '
    '  SELECT * '
    '  FROM uespulses WHERE uesid IN (SELECT DISTINCT uesid FROM k_uesidfunctionmap WHERE activeflag = "Y") '
    '  GROUP BY uesid, seq, frame;  ',

    'ALTER TABLE k_brands ADD PRIMARY KEY (brandid); ',

    'ALTER TABLE k_codesets ADD PRIMARY KEY (brandid, devicetypeid, codesetid); ',

    'ALTER TABLE k_devicetypes ADD PRIMARY KEY (devicetypeid); ',

    'ALTER TABLE k_functions ADD PRIMARY KEY (id); ',
    'ALTER TABLE k_functions ADD INDEX functionname (functionname); ',

    'ALTER TABLE k_uescodes ADD PRIMARY KEY (uesid); ',

    'ALTER TABLE k_uesidfunctionmap ADD PRIMARY KEY (uesid, codesetid, functionid); ',

    'ALTER TABLE k_uespulses ADD PRIMARY KEY (uesid, seq, frame); '

    ]


def executions(cnx, sql):
    for ea in sql:
        try:
            cnx.cursor.execute(ea)
        except Exception, e:
            print e


def k_codesets(cnx, brands):
    try:
        sql = ('CREATE TABLE k_codesets AS '
               '  SELECT * from codesets '
               '  WHERE activeflag = "Y" '
               '  AND ((devicetypeid = %d AND brandid IN (%s)) OR (devicetypeid = %d AND brandid IN (%s))) '
               '  GROUP BY brandid, devicetypeid, codesetid; '
               #'  AND rank < 999 '
               '  ; '
               % (brands[0][0], brands[0][1], brands[1][0], brands[1][1]))
        cnx.cursor.execute(sql)
    except Exception, e:
        print e


def k_brands(cnx, brands):
    try:
        sql = ('CREATE TABLE k_brands AS '
               '  SELECT brandid, brandname '
               '  FROM brands '
               '  WHERE (brandid IN (%s)) OR (brandid IN (%s)) '
               '  GROUP BY brandid; '
               % (brands[0][1], brands[1][1]))
        cnx.cursor.execute(sql)
    except Exception, e:
        print e


def main():
    try:
        #log = ir.Logger('sqlite')
        #cnx = ir.DBConnection()
        cnx = ir.DBConnection(host='54.254.101.29', user='kai', passwd='p33lz3l')
        k_brands(cnx, selection)
        k_codesets(cnx, selection)
        executions(cnx, queries)
    except Exception, e:
        print e

if __name__ == '__main__':
    start_time = datetime.datetime.now()
    main()
    end_time = datetime.datetime.now()
    print "Duration: from %s to %s (%s)." % (start_time, end_time, (end_time - start_time))
