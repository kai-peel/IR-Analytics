#!/usr/bin/python
#__author__ = 'kai'
#__version__ = '1.0'
#__date__ = '2015-11-09'
import datetime
from utils import irutils as ir
import AesCrypt
import sel_sqlite as tset
"""
sel_brands = [[1, '13, 24, 30, 31, 37, 39, 41, 42, 46, 50'],
              [2, '121,137,149,137,123,137,183,137,540,137,379,137,410,137,194,120,432,37,120,380,37,134,128,194,137']
              ]

sel_codesets = '100005,100012,190032,100002,190027,100043,190076,1000993,100130,100038,1004193,190051,1001774,100043,' \
               '100030, 190148,1000708,1001926,190153,180131,11004343,1004190,190018,190091,1001395,191691,100080,' \
               '192785,191704,190108, 1000646,11004428,190154,1001868,191608,11004344,1004191,190077,1001239,100193,' \
               '191578,191781,190039,1001769,100189, 1000676,190028,100003,190239,1001271,180135,190161,1000970,' \
               '190155,1003000,191582,191694,11004832,10004293,100036, 190184,190118,190211,1001621,11004354,' \
               '11004365,191604,100040,190189,1000975,11004830,190052,100066,190242,191581,191677,191593,100054,' \
               '191801,190351,180182,190221,190219,190116,1000928,191776,191825,191787,191834,192753,192768,1004752,' \
               '1000996,191782,191866,192753,190208,191751,191603,190207,191777,190135,190209,1001772,191563,1003160,' \
               '191606,1000703,100159,191778,190109,1005144,191706,191683'
"""
queries = [
    #'CREATE TABLE k_devicetypes AS '
    #'  SELECT devicetypeid, devicetype '
    #'  FROM devicetypes WHERE devicetypeid IN (SELECT DISTINCT devicetypeid FROM k_codesets WHERE activeflag = "Y") '
    #'  GROUP BY devicetypeid;  ',

    'CREATE TABLE k_uesidfunctionmap AS '
    '  SELECT uesid, codesetid, functionid, origfunctionid, activeflag '
    '  FROM uesidfunctionmap WHERE activeflag = "Y" AND codesetid IN (SELECT codesetid FROM k_codesets) '
    '  GROUP BY uesid, codesetid, functionid;  ',

    'CREATE TABLE k_uescodes AS '
    '  SELECT uesid, codesetid, repeatcount, codetype, frequency, activeflag, encodedbinary, '
    '  syscode, datacode, format, encodedbinary2 '
    '  FROM uescodes WHERE uesid IN (SELECT uesid FROM k_uesidfunctionmap WHERE activeflag = "Y") '
    '  GROUP BY uesid;  ',

    'CREATE TABLE k_functions AS '
    '  SELECT id, functionname, functionclass, displayname '
    '  FROM functions WHERE id IN (SELECT functionid FROM k_uesidfunctionmap WHERE activeflag = "Y") '
    '  GROUP BY id;  '
    ]

post_queries = [
    #'ALTER TABLE k_brands ADD PRIMARY KEY (brandid); ',
    #'ALTER TABLE k_devicetypes ADD PRIMARY KEY (devicetypeid); ',
    'ALTER TABLE k_codesets ADD PRIMARY KEY (brandid, devicetypeid, codesetid); ',

    'ALTER IGNORE TABLE k_uesidfunctionmap ADD PRIMARY KEY (uesid, codesetid, functionid); ',

    'ALTER TABLE k_uescodes DROP COLUMN codesetid, DROP COLUMN repeatcount, DROP COLUMN codetype, '
    '  DROP COLUMN frequency, DROP COLUMN encodedbinary, '
    '  DROP COLUMN syscode, DROP COLUMN datacode, DROP COLUMN format, DROP COLUMN encodedbinary2; ',
    'ALTER TABLE k_uescodes ADD PRIMARY KEY (uesid); ',

    'ALTER TABLE k_functions DROP COLUMN functionname, DROP COLUMN functionclass, DROP COLUMN displayname; ',
    'ALTER TABLE k_functions ADD PRIMARY KEY (id); ',
    #'ALTER TABLE k_functions ADD INDEX functionname (functionname); ',

    'CREATE TABLE k_uespulses AS '
    '  SELECT * '
    '  FROM uespulses WHERE uesid IN (SELECT uesid FROM k_uesidfunctionmap WHERE activeflag = "Y") '
    '  GROUP BY uesid, seq, frame;  ',

    'ALTER TABLE k_uespulses ADD PRIMARY KEY (uesid, seq, frame); '
    ]


def executions(log, cnx, sql):
    for ea in sql:
        try:
            log.write('Execute: %s.\n\n' % ea)
            print('Execute: %s.\n' % ea)
            cnx.cursor.execute(ea)
        except Exception, e:
            print e


def k_codesets(log, cnx, brands, codesets):
    try:
        sql = ('CREATE TABLE k_codesets AS '
               '  SELECT brandid, devicetypeid, codesetid, rank, activeflag from codesets '
               '  WHERE activeflag = "Y" '
               '  AND ((devicetypeid = %d AND brandid IN (%s) AND rank < 999) '
               #'  AND ((devicetypeid = %d AND brandid IN (%s)) '
               '    OR (devicetypeid = %d AND brandid IN (%s) AND rank < 999) '
               #'    OR (devicetypeid = %d AND brandid IN (%s)) '
               '    OR (codesetid IN (%s))) '
               '  GROUP BY brandid, devicetypeid, codesetid; '
               '  ; '
               % (brands[0][0], brands[0][1], brands[1][0], brands[1][1], codesets))
        log.write('Execute: %s.\n\n' % sql)
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


def purge_uesfunctionmap(log, cnx, uesid, codetype, syscode, datacode, fmt, encodedbinary2):
    try:
        sql = ('SELECT uesid FROM k_uescodes a '
               '  WHERE uesid != %d '
               '  AND codetype = "%s" '
               '  AND format = "%s" '
               '  AND syscode = %d '
               '  AND datacode = %d '
               '  AND encodedbinary2 = "%s"; '
               % (uesid, codetype, fmt, syscode, datacode, encodedbinary2))
        cnx.cursor.execute(sql)
        rows = cnx.cursor.fetchall()
        uesids = ''
        for ea in rows:
            uesids += ("%s," % str(ea[0]))
        uesids = uesids[:-1]
        log.write('Merge (%s) with %d.\n' % (uesids, uesid))
        print('Merge (%s) with %d.' % (uesids, uesid))

        sql = ('UPDATE k_uesidfunctionmap '
               '  SET origfunctionid = uesid, uesid = %d '
               '  WHERE uesid IN (%s); '
               % (uesid, uesids))
        cnx.cursor.execute(sql)

        sql = ('DELETE FROM k_uescodes '
               '  WHERE uesid IN (%s); '
               % uesids)
        cnx.cursor.execute(sql)

        cnx.db.commit()
    except Exception, e:
        print e


def purge_uescodes(log, cnx):
    try:
        sql = ('SELECT uesid, codetype, syscode, datacode, format, encodedbinary2 FROM k_uescodes a '
               '  JOIN k_usage b ON b.codeset = a.codesetid '
               '  WHERE encodedbinary2 IS NOT NULL AND encodedbinary2 != "" '
               '  GROUP BY codetype, format, syscode, datacode, encodedbinary2 '
               '  HAVING count(*) > 1 ORDER BY b.cnt desc; ')
        cnx.cursor.execute(sql)
        rows = cnx.cursor.fetchall()
        for ea in rows:
            purge_uesfunctionmap(log, cnx, ea[0], ea[1], ea[2], ea[3], ea[4], ea[5])
    except Exception, e:
        print e


def encrypt_functions(log, cnx, tbl):
    try:
        sql = ('ALTER IGNORE TABLE %s ADD daw VARCHAR(255);' % tbl)
        cnx.cursor.execute(sql)
    except Exception, e:
        print e

    try:
        sql = ('SELECT id, IFNULL(functionname, ""), IFNULL(functionclass, ""), IFNULL(displayname, "") from %s;' % tbl)
        cnx.cursor.execute(sql)
        rows = cnx.cursor.fetchall()
        c = AesCrypt.AesCrypt256()
        for ea in rows:
            daw = c.encryptB64('|'.join(ea[1:]))
            clear = c.decryptB64(daw)
            log.write('%d: %s, %s.\n' % (ea[0], daw, clear))
            print('%d: %s, %s.' % (ea[0], daw, clear))
            try:
                #sql = ('UPDATE %s SET daw = "%s" WHERE id = %d;' % (tbl, daw, ea[0]))
                sql = ('UPDATE %s SET daw = "%s" WHERE id = %d;' % (tbl, clear, ea[0]))
                cnx.cursor.execute(sql)
            except Exception, e:
                print e
        cnx.db.commit()
        log.flush()
    except Exception, e:
        print e


def encrypt_uescodes(log, cnx, tbl):
    try:
        sql = ('ALTER IGNORE TABLE %s ADD daw VARCHAR(255);' % tbl)
        cnx.cursor.execute(sql)
    except Exception, e:
        print e
    try:
        sql = ('SELECT uesid, IFNULL(repeatcount, ""), IFNULL(codetype, ""), IFNULL(frequency, ""), IFNULL(encodedbinary, "") from %s; ' % tbl)
        cnx.cursor.execute(sql)
        rows = cnx.cursor.fetchall()
        c = AesCrypt.AesCrypt256()
        for ea in rows:
            daw = c.encryptB64('|'.join(ea[1:]))
            clear = c.decryptB64(daw)
            log.write('%d: %s, %s.\n' % (ea[0], daw, clear))
            print('%d: %s, %s.' % (ea[0], daw, clear))
            try:
                #sql = ('UPDATE %s SET daw = "%s" WHERE uesid = %d;' % (tbl, daw, ea[0]))
                sql = ('UPDATE %s SET daw = "%s" WHERE uesid = %d;' % (tbl, clear, ea[0]))
                cnx.cursor.execute(sql)
            except Exception, e:
                print e
        cnx.db.commit()
        log.flush()
    except Exception, e:
        print e


def main():
    try:
        f = ir.Logger('sqlite', 1)
        #cnx = ir.DBConnection()
        cnx = ir.DBConnection(host='54.254.101.29', user='kai', passwd='p33lz3l')
        #k_brands(cnx, selection)
        k_codesets(f.logs[0], cnx, tset.sel_brands, tset.sel_codesets)
        executions(f.logs[0], cnx, queries)
        purge_uescodes(f.logs[0], cnx)
        #encrypt_functions(f.logs[0], cnx, 'k_functions')
        #encrypt_uescodes(f.logs[0], cnx, 'k_uescodes')
        #executions(f.logs[0], cnx, post_queries)
    except Exception, e:
        print e

if __name__ == '__main__':
    start_time = datetime.datetime.now()
    print "Started: at %s." % start_time
    main()
    end_time = datetime.datetime.now()
    print "Duration: from %s to %s (%s)." % (start_time, end_time, (end_time - start_time))
