##  @file update brandtypemap
#   @brief add newly ingested brands into brandtypemap.
__version__ = "1.0.0"
__date__ = "05-DEC-2014"
from utils import irutils


def clean_brandtypemap(log, cnx):
    query = ("SELECT a.brandid, a.devicetypeid from brandtypemap a "
             "LEFT JOIN codesets b on a.brandid=b.brandid and a.devicetypeid=b.devicetypeid and activeflag='Y' "
             "WHERE b.codesetid IS NULL AND a.devicetypeid < 100 "
             "GROUP BY a.brandid, a.devicetypeid ")
    try:
        cnx.cursor.execute(query)
        btmap = cnx.cursor.fetchall()
        do_commit = False
        for each in btmap:
            log.write("deleting brandid=%d and devicetypeid=%d..." % (each[0], each[1]))
            query = ("DELETE FROM brandtypemap "
                     "WHERE brandid=%d AND devicetypeid=%d "
                     % (each[0], each[1]))
            try:
                cnx.cursor.execute(query)
                do_commit = True
            except Exception, e:
                print e
        if do_commit:
            cnx.db.commit()
    except Exception, e:
        print "ERR:clean_brandtypemap:%s." % e


def clean_countriesbrandtypemap(log, cnx):
    query = ("SELECT a.brandid, a.devicetypeid from countriesbrandtypemap a "
             "LEFT JOIN codesets b on a.brandid=b.brandid and a.devicetypeid=b.devicetypeid and activeflag='Y' "
             "WHERE b.codesetid IS NULL AND a.devicetypeid < 100 "
             "GROUP BY a.brandid, a.devicetypeid ")
    try:
        cnx.cursor.execute(query)
        btmap = cnx.cursor.fetchall()
        do_commit = False
        for each in btmap:
            log.write("deleting brandid=%d and devicetypeid=%d..." % (each[0], each[1]))
            query = ("DELETE FROM countriesbrandtypemap "
                     "WHERE brandid=%d AND devicetypeid=%d "
                     % (each[0], each[1]))
            try:
                cnx.cursor.execute(query)
                do_commit = True
            except Exception, e:
                print e
        if do_commit:
            cnx.db.commit()
    except Exception, e:
        print "ERR:clean_countriesbrandtypemap:%s." % e


##  @fn
#   @brief
#
def update_brandtypemap(log, cnx, dtype):
    query = ("INSERT INTO brandtypemap (brandid, devicetypeid, rank, timestamp) "
             "SELECT brandid, devicetypeid, 999, CURRENT_TIMESTAMP FROM codesets s "
             "WHERE s.brandid NOT IN (SELECT brandid from brandtypemap where devicetypeid=%d) "
             "AND activeflag='Y' AND devicetypeid=%d GROUP BY brandid " %
             (dtype, dtype))
    try:
        cnx.cursor.execute(query)
        cnx.db.commit()

    except Exception, e:
        print "ERR:update_brandtypemap:%s." % e


##  @fn
#   @brief
#
def get_devicetypes(log, cnx):
    query = "SELECT DISTINCT devicetypeid from devicetypes "
    try:
        cnx.cursor.execute(query)
        devices = cnx.cursor.fetchall()
        for row in devices:
            print "checking device type = %d" % row[0]
            update_brandtypemap(log, cnx, row[0])

    except Exception, e:
        print "ERR:get_devicetypes:%s." % e


def main():
    log = irutils.Logger("btm")
    cnx = irutils.DBConnection()
    #cnx = irutils.DBConnection(host='54.254.101.29', user='kai', passwd='p33lz3l')
    get_devicetypes(log, cnx)
    clean_brandtypemap(log, cnx)
    clean_countriesbrandtypemap(log, cnx)

if __name__ == '__main__':
    main()
