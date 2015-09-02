from utils import irutils


def get_ir_stream(cnx, uesid):
    try:
        cnx.cursor.execute("SELECT pulse FROM uespulses where uesid=%d order by seq " % uesid)
        p = cnx.cursor.fetchall()
        pulse = []
        for each in p:
            pulse.append(str(each[0]))

        #print pulse
        return pulse

    except Exception, e:
        print e


def csprt(cnx, log, src, dest):
    try:
        for each in src:
            pulse = get_ir_stream(cnx, each[0])
            log.write("%d|%s|%s|%s|%s|\n" % (dest, each[1], each[2], each[3], ','.join(pulse)))
    except Exception, e:
        print e


def main(dest, src):
    log = irutils.Logger("cscpy")
    cnx = irutils.DBConnection()
    #log.write("%s|%s|%s|%s|%s|%s|%s|%s\n" % ("Function", "Identical", "ID1", "Freq1", "Repeat1", "ID2", "Freq2", "Repeat2"))
    #190248|40000|Partial_Repeat|Power|10,72,10,72,10,72,10,32,10,32,10,32,10,32,10,32,10,32,10,32,10,936|10,72,10,72,10,72,10,32,10,32,10,32,10,72,100,4000|

    try:
        query = ("SELECT a.uesid, b.frequency, b.codetype, c.functionname FROM uesidfunctionmap a, uescodes b, functions c "
                 "WHERE a.uesid=b.uesid AND a.functionid=c.id AND a.activeflag ='Y' "
                 "AND a.codesetid=%d " % src)
        cnx.cursor.execute(query)
        cs = cnx.cursor.fetchall()

        """
        query = ("SELECT uesid, functionid FROM uesidfunctionmap "
                 "WHERE activeflag ='Y' "
                 "AND codesetid=%d " % src)
        cnx.cursor.execute(query)
        cssrc = cnx.cursor.fetchall()
        """
        csprt(cnx, log, cs, dest)
    except Exception, e:
        print e

if __name__ == '__main__':
    main(290833, 290013)
