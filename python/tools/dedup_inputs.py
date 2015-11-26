import datetime
from utils import irutils as ir


def remove_dup_inputs(log, cnx, rows):
    try:
        for ea in rows:
            uesid = ea[0]
            codesetid = ea[1]
            encodedbinary2 = ea[2]
            fmt = ea[3]
            syscode = ea[4]
            datacode = ea[5]
            functionid = ea[6]
            sql = ('UPDATE uesidfunctionmap a '
                   '  JOIN uescodes b ON b.uesid = a.uesid '
                   #'    AND b.format = "%s" AND b.encodedbinary2 = "%s" AND b.syscode = %d AND b.datacode = %d '
                   '    AND b.format = "%s" AND b.syscode = %d AND b.datacode = %d '
                   '  JOIN functions c ON c.id = a.functionid AND c.functionclass = "InputSelection" '
                   '  SET a.activeflag = "D", a.updatedby = "kai", a.comments = "Duplicate %d." '
                   '  WHERE a.activeflag = "Y" '
                   '  AND a.codesetid = %d AND (a.uesid <> %d OR a.functionid <> %d); '
                   % (fmt, syscode, datacode, uesid, codesetid, uesid, functionid))
            cnx.cursor.execute(sql)
            log.write('%s.\n' % sql)
            print fmt, codesetid, uesid, sql
        cnx.db.commit()
        log.flush()
    except Exception, e:
        print e


def find_dup_inputs(log, cnx):
    try:
        sql = ('SELECT a.uesid, a.codesetid, b.encodedbinary2, b.format, b.syscode, b.datacode, a.functionid, count(*) '
               '  FROM uesidfunctionmap a '
               '  JOIN uescodes b ON b.uesid = a.uesid '
               '  JOIN functions c ON c.id = a.functionid '
               '  WHERE a.activeflag = "Y" '
               '  AND c.functionclass = "InputSelection" '
               '  AND b.format IS NOT NULL AND b.format <> "" '
               '  AND b.encodedbinary2 IS NOT NULL AND b.encodedbinary2 <> "" '
               '  AND b.frequency < 100000 AND (b.syscode <> 0 OR b.datacode <> 0) '
               #'  GROUP BY a.codesetid, b.encodedbinary2, b.format, b.syscode, b.datacode '
               '  GROUP BY a.codesetid, b.format, b.syscode, b.datacode '
               '  HAVING COUNT(*) > 1; ')
        cnx.cursor.execute(sql)
        return cnx.cursor.fetchall()
    except Exception, e:
        print e


def main():
    try:
        f = ir.Logger('input', 1)
        cnx = ir.DBConnection()
        #cnx = ir.DBConnection(host='54.254.101.29', user='kai', passwd='p33lz3l')
        rows = find_dup_inputs(f.logs[0], cnx)
        remove_dup_inputs(f.logs[0], cnx, rows)
    except Exception, e:
        print e

if __name__ == '__main__':
    start_time = datetime.datetime.now()
    print "Started: at %s." % start_time
    main()
    end_time = datetime.datetime.now()
    print "Duration: from %s to %s (%s)." % (start_time, end_time, (end_time - start_time))
