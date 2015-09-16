__version__ = "1.0.0"
__date__ = "10-SEP-2015"

from utils import irutils as ir


def ac_temp_lookup(log, cnx, codesetid, uesid, functionid, encodedbinary):
    query = ("SELECT m.uesid, m.functionid, f.functionname from uesidfunctionmap m "
             "JOIN uescodes c ON c.uesid = m.uesid "
             "JOIN functions f ON f.id = m.functionid "
             "WHERE m.functionid > 5000 "
             "AND m.codesetid = %d "
             "AND m.activeflag = 'Y' "
             "AND c.encodedbinary2 = '%s'; "
             % (codesetid, encodedbinary))
    try:
        cnx.cursor.execute(query)
        rows = cnx.cursor.fetchall()
        for each in rows:
            log.pout("%d|%d|%d|%s|%d|%d|%s" % (codesetid, uesid, functionid, encodedbinary, each[0], each[1], each[2]))

    except Exception, e:
        print e


def main():
    log = ir.Logger("pwr")
    log.out.write("codesetid|uesid|functionid|encodedbinary2|uesid2|fid2|functionname\n")

    cnx = ir.DBConnection()
    query = ("SELECT m.codesetid, m.uesid, m.functionid, c.encodedbinary2, m.origfunctionid from uesidfunctionmap m "
             "JOIN codesets s ON s.codesetid = m.codesetid "
             "JOIN uescodes c ON c.uesid = m.uesid "
             "WHERE m.functionid IN (23, 332) "
             "AND m.activeflag = 'Y' AND s.activeflag = 'Y' "
             "AND s.devicetypeid = 18 "
             "GROUP BY m.codesetid, m.functionid; ")

    badsets = set([690595, 690845, 690884, 690891, 691065, 691089, 880742, 880743, 880744, 880745, 880746, 880747, 880748, 880749, 880752, 880755, 880756, 880757, 880759])

    try:
        cnx.cursor.execute(query)
        rows = cnx.cursor.fetchall()
        for each in rows:
            print each[0], ':', each[1], ':', each[2]
            origfunctionid = each[4]
            if each[0] not in badsets and origfunctionid != 6216 and origfunctionid != 5878 and each[3] != '0':
                ac_temp_lookup(log, cnx, each[0], each[1], each[2], each[3])
    except Exception, e:
        print e


if __name__ == '__main__':
    main()
