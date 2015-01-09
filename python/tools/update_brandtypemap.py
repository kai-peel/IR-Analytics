##  @file update brandtypemap
#   @brief add newly ingested brands into brandtypemap.
__version__ = "1.0.0"
__date__ = "05-DEC-2014"
from utils import irutils


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
    get_devicetypes(log, cnx)


if __name__ == '__main__':
    main()
