#!/usr/bin/python
from utils import irutils as ir
import datetime
__author__ = 'kai'
__version__ = '1.0'
__date__ = '2015-11-02'


def getUESIdsForFunction(cnx, functionname, devicetypeid, brandid, countryCode='US', lang='en', version='V2'):
    try:
        sql = (
            "SELECT b.id functionid, functionname, b.displayname AS displayname, a.uesid, a.codesetid, c.rank rank, "
            "IFNULL(functionclass,'UNCLASSIFIED') functionclass,encodedbinary , 'aa' AS country "
            "FROM uescodes a "
            "JOIN codesets c ON (devicetypeid = %d AND brandid = %d AND c.activeflag = 'Y') "
            "JOIN uesidfunctionmap d ON (d.codesetid = c.codesetid AND d.uesid = a.uesid AND d.activeflag = 'Y') "
            "JOIN functions b ON (b.functionname = '%s' AND d.functionid = b.id); "
            % (devicetypeid, brandid, functionname)
        )
        cnx.cursor.execute(sql)
        rows = cnx.cursor.fetchall()
        print rows

    except Exception, e:
        print 'getUESIdsForFunction::%s' % e


def getUesIdsForCodeset(cnx, codesetid):
    try:
        sql = (
            " SELECT b.id functionid, functionname, b.displayname AS displayname, c.uesid, b.grouprank rank, IFNULL(functionclass,'UNCLASSIFIED') functionclass "
			" FROM uesidfunctionmap c, functions b "
			" WHERE c.codesetid = %d AND c.functionid = b.id AND c.activeflag = 'Y' "
			" UNION ALL "
			" SELECT b.id, b.functionname, b.displayname AS displayname, a.uesid ues, b.grouprank rank, IFNULL(functionclass,'TIMER') functionclass "
			" FROM uescodes a, uesidfunctionmap c ,functions b "
			" WHERE c.uesid=a.uesid AND c.functionid = b.id AND c.codesetid = 900000 AND c.functionid = 651 "
			" UNION "
			" SELECT b.id, b.functionname, b.displayname, a.uesid ues, IFNULL(b.grouprank,999) rank, b.functionclass "
			" FROM uescodes a, uesidfunctionmap e, codesets c, codesets d, functions b "
			" WHERE e.functionid = b.id AND e.codesetid = %d "
			" AND d.codesetid <> c.codesetid AND c.devicetypeid = d.devicetypeid AND c.brandid = d.brandid AND c.activeflag = 'Y' AND d.activeflag = 'Y' "
			" AND e.codesetid = d.codesetid AND e.functionid = b.id AND b.functionclass = 'Inputselection' AND b.functionname <> 'Input' AND e.uesid = a.uesid; "
            % (codesetid, codesetid)
        )
        cnx.cursor.execute(sql)
        rows = cnx.cursor.fetchall()
        print rows

    except Exception, e:
        print 'getUesIdsForCodeset::%s' % e


if __name__ == '__main__':
    cnx = ir.DBConnection(host='127.0.0.1')
    #cnx = ir.DBConnection()

    start_time = datetime.datetime.now()
    print "Started: %s." % start_time
    getUESIdsForFunction(cnx, 'Power', 1, 37)
    end_time = datetime.datetime.now()
    print "Duration: from %s to %s (%s)." % (start_time, end_time, (end_time - start_time))

    start_time = datetime.datetime.now()
    print "Started: %s." % start_time
    getUesIdsForCodeset(cnx, 290013)
    end_time = datetime.datetime.now()
    print "Duration: from %s to %s (%s)." % (start_time, end_time, (end_time - start_time))
