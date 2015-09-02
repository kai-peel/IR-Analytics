from utils import irutils


def get_ir_stream(cnx, uesid):
    try:
        cnx.cursor.execute("SELECT frequency, repeatcount FROM uescodes where uesid=%d " % uesid)
        f = cnx.cursor.fetchall()
        freq = f[0][0]
        rpt = f[0][1]

        cnx.cursor.execute("SELECT pulse FROM uespulses where uesid=%d order by seq " % uesid)
        p = cnx.cursor.fetchall()
        pulse = []
        for each in p:
            pulse.append(str(each[0]))

        print freq, rpt, pulse
        return freq, rpt, pulse

    except Exception, e:
        print e


def keycmp(cnx, log, funcid, dest, src):
    print dest, src
    (freq1, rpt1, pulse1) = get_ir_stream(cnx, dest)
    (freq2, rpt2, pulse2) = get_ir_stream(cnx, src)

    r = 'Fail'
    if pulse1 == pulse2:
        r = 'OK'
    log.write("%d|%s|%d|%s|%s|%d|%s|%s\n" %
              (funcid, r, dest, freq1, rpt1, src, freq2, rpt2))


def cscmp(cnx, log, dest, srccsid):
    try:
        for each in dest:
            print each
            query = ("SELECT uesid FROM uesidfunctionmap "
                     "WHERE activeflag ='Y' AND codesetid=%d AND functionid=%d "
                     % (srccsid, each[1]))
            cnx.cursor.execute(query)
            uesid = cnx.cursor.fetchone()
            if uesid and len(uesid) > 0:
                keycmp(cnx, log, each[1], each[0], uesid[0])
            else:
                log.write("%d|%s|%d|||||\n" % (each[1], "Missing", each[0]))
    except Exception, e:
        print e


def main(dest, src):
    log = irutils.Logger("cscmp")
    cnx = irutils.DBConnection()
    log.write("%s|%s|%s|%s|%s|%s|%s|%s\n" % ("Function", "Identical", "ID1", "Freq1", "Repeat1", "ID2", "Freq2", "Repeat2"))

    try:
        query = ("SELECT uesid, functionid FROM uesidfunctionmap "
                 "WHERE activeflag ='Y' "
                 "AND codesetid=%d ORDER BY functionid " % dest)
        cnx.cursor.execute(query)
        csdest = cnx.cursor.fetchall()

        """
        query = ("SELECT uesid, functionid FROM uesidfunctionmap "
                 "WHERE activeflag ='Y' "
                 "AND codesetid=%d " % src)
        cnx.cursor.execute(query)
        cssrc = cnx.cursor.fetchall()
        """
        cscmp(cnx, log, csdest, src)
    except Exception, e:
        print e

if __name__ == '__main__':
    main(290013, 290831)
