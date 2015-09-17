#!/usr/bin/python
__author__ = 'kai'
__version__ = '1.0'
__date__ = '15-Sep-2015'
from utils import irutils as ir

"""
import MySQLdb
class DBConnection:
    def __init__(self, host='54.254.101.29', db='devices', user='kai', passwd='p33lz3l'):
        try:
            self.db = MySQLdb.connect(host=host, user=user, passwd=passwd, db=db, charset="utf8", use_unicode=True)
            self.cursor = self.db.cursor()
        except Exception, e:
            print "ERR:DBConnection:__init__: %s" % e

    def __del__(self):
        try:
            self.cursor.close()
            self.db.close()
        except Exception, e:
            print "ERR:DBConnection:__del__: %s" % e
"""


# \fn level1
# \note
#   !!! query only intend to provide correct logic, not optimized for speed and performance. !!!
#   !!! for simplification, only "power" key supported. !!!
#   !!! before enter production, both "power" and "poweron" need to be supported. !!!
#
# @param[in] devicetypeid
# @param[in] brandid
# @param[in] country
# @param[in] functionid
#
def get_level1_count(cnx, devicetypeid, brandid, functions):
    try:
        return len(level1(cnx, devicetypeid, brandid, functions))

    except Exception, e:
        print 'get_level1_count::%s' % e


# \fn level1
# \note
#   !!! query only intend to provide correct logic, not optimized for speed and performance. !!!
#   !!! for simplification, only "power" key supported. !!!
#   !!! before enter production, both "power" and "poweron" need to be supported. !!!
#
# @param[in] devicetypeid
# @param[in] brandid
# @param[in] country
# @param[in] functionid
#
def level1(cnx, devicetypeid, brandid, functions):
    try:
        funcs = functions.split(',')
        if len(funcs) > 1:
            functionids = []
            for each in funcs:
                functionids.append(int(each))
            return level1_multi(cnx, devicetypeid, brandid, None, functionids)
        else:
            return level1_single(cnx, devicetypeid, brandid, None, int(funcs[0]))

    except Exception, e:
        print 'level1::%s' % e


# \fn level1
# \note
#   !!! query only intend to provide correct logic, not optimized for speed and performance. !!!
#   !!! for simplification, only "power" key supported. !!!
#   !!! before enter production, both "power" and "poweron" need to be supported. !!!
#
# @param[in] devicetypeid
# @param[in] brandid
# @param[in] country
# @param[in] functionid
#
def level1_single(cnx, devicetypeid, brandid, country, functionid):
    try:
        # test if this is a global or localized ranking
        if country is None:
            # use global ranking.
            query = ("SELECT order_by_rank.* FROM "
                     "( "
                     "SELECT a.codesetid, a.uesid, b.encodedbinary, c.rank FROM uesidfunctionmap a "
                     "JOIN uescodes b ON b.uesid = a.uesid "
                     "JOIN codesets c ON c.codesetid = a.codesetid "
                     "WHERE a.activeflag = 'Y' AND c.activeflag = 'Y' "  # only if both codeset and keycode are "active".
                     "AND c.devicetypeid = %d "  # @param[in] devicetypeid
                     "AND c.brandid = %d "  # @param[in] brandid
                     "AND a.functionid = %d "  # @param[in] functionid
                     "ORDER BY c.rank "  # rank by global.
                     ") AS order_by_rank "
                     "GROUP BY order_by_rank.encodedbinary "  # remove duplicated based on encoded binary value.
                     "ORDER by order_by_rank.rank "
                     % (devicetypeid, brandid, functionid))
        else:
            # use localized ranking.
            query = ("SELECT order_by_rank.* FROM "
                     "( "
                     "SELECT a.codesetid, a.uesid, b.encodedbinary, c.rank AS grank, d.rank AS lrank, "
                     "IF(d.rank, d.rank, c.rank+5) AS ranking "  # local ranking promotion.
                     "FROM uesidfunctionmap a "
                     "JOIN uescodes b ON b.uesid = a.uesid "
                     "JOIN codesets c ON c.codesetid = a.codesetid "
                     "LEFT OUTER JOIN countrycodesetmap d ON d.codesetid = a.codesetid "
                     "WHERE a.activeflag = 'Y' AND c.activeflag = 'Y' "  # only if both codeset and keycode are "active".
                     "AND c.devicetypeid = %d "  # @param[in] devicetypeid
                     "AND c.brandid = %d "  # @param[in] brandid
                     "AND a.functionid = %d "  # @param[in] functionid
                     "ORDER BY ranking "  # rank by promoting local by 5.
                     ") AS order_by_rank "
                     "GROUP BY order_by_rank.encodedbinary "  # remove duplicated based on encoded binary value.
                     "ORDER by order_by_rank.ranking "
                     % (devicetypeid, brandid, functionid))

        cnx.cursor.execute(query)
        return cnx.cursor.fetchall()

    except Exception, e:
        print 'level1_single::%s' % e


# \fn level1_each
# \note
#   !!! query only intend to provide correct logic, not optimized for speed and performance. !!!
#   !!! for simplification, only "power" key supported. !!!
#   !!! before enter production, both "power" and "poweron" need to be supported. !!!
#
# @param[in] devicetypeid
# @param[in] brandid
# @param[in] country
# @param[in] functionid, one key only
# @param[in] excludes, codesetids to be excluded for output.
#
def level1_each(cnx, devicetypeid, brandid, country, functionid, excludes):
    try:
        codesets = ''
        # construct exclusion list for next functionid lookup.
        query = ("SELECT DISTINCT a.codesetid FROM uesidfunctionmap a "
                 "JOIN codesets c ON c.codesetid = a.codesetid "
                 "WHERE a.activeflag = 'Y' AND c.activeflag = 'Y' "  # only if both codeset and keycode are "active".
                 "AND c.devicetypeid = %d "  # @param[in] devicetypeid
                 "AND c.brandid = %d "  # @param[in] brandid
                 "AND a.functionid = %d "  # @param[in] functionid
                 "AND a.codesetid NOT IN (%s) "  # @param[in] excludes
                 % (devicetypeid, brandid, functionid, excludes))

        cnx.cursor.execute(query)
        rows = cnx.cursor.fetchall()
        for each in rows:
            codesets += ',' + str(each[0])
        #print codesets

        # test if this is a global or localized ranking
        if country is None:
            # use global ranking.
            query = ("SELECT order_by_rank.* FROM "
                     "( "
                     "SELECT a.codesetid, a.uesid, a.functionid, b.encodedbinary, c.rank FROM uesidfunctionmap a "
                     "JOIN uescodes b ON b.uesid = a.uesid "
                     "JOIN codesets c ON c.codesetid = a.codesetid "
                     "WHERE a.activeflag = 'Y' AND c.activeflag = 'Y' "  # only if both codeset and keycode are "active".
                     "AND c.devicetypeid = %d "  # @param[in] devicetypeid
                     "AND c.brandid = %d "  # @param[in] brandid
                     "AND a.functionid = %d "  # @param[in] functionid
                     "AND a.codesetid NOT IN (%s) "  # @param[in] excludes
                     "ORDER BY c.rank "  # rank by global.
                     ") AS order_by_rank "
                     "GROUP BY order_by_rank.encodedbinary "  # remove duplicated based on encoded binary value.
                     "ORDER by order_by_rank.rank "
                     % (devicetypeid, brandid, functionid, excludes))
        else:
            # use localized ranking.
            query = ("SELECT order_by_rank.* FROM "
                     "( "
                     "SELECT a.codesetid, a.uesid, a.functionid, b.encodedbinary, c.rank AS grank, d.rank AS lrank, "
                     "IF(d.rank, d.rank, c.rank+5) AS ranking "  # local ranking promotion.
                     "FROM uesidfunctionmap a "
                     "JOIN uescodes b ON b.uesid = a.uesid "
                     "JOIN codesets c ON c.codesetid = a.codesetid "
                     "LEFT OUTER JOIN countrycodesetmap d ON d.codesetid = a.codesetid "
                     "WHERE a.activeflag = 'Y' AND c.activeflag = 'Y' "  # only if both codeset and keycode are "active".
                     "AND c.devicetypeid = %d "  # @param[in] devicetypeid
                     "AND c.brandid = %d "  # @param[in] brandid
                     "AND a.functionid = %d "  # @param[in] functionid
                     "AND a.codesetid NOT IN (%s) "  # @param[in] excludes
                     "ORDER BY ranking "  # rank by promoting local by 5.
                     ") AS order_by_rank "
                     "GROUP BY order_by_rank.encodedbinary "  # remove duplicated based on encoded binary value.
                     "ORDER by order_by_rank.ranking "
                     % (devicetypeid, brandid, functionid, excludes))

        cnx.cursor.execute(query)
        rows = cnx.cursor.fetchall()
        """
        print '\nitem count: ', len(rows)
        for each in rows:
            print each
        """
        return rows

    except Exception, e:
        print 'level1_each::%s' % e


# \fn level1_all
# \note
#   !!! query only intend to provide correct logic, not optimized for speed and performance. !!!
#   !!! for simplification, only "power" key supported. !!!
#   !!! before enter production, both "power" and "poweron" need to be supported. !!!
#
# @param[in] devicetypeid
# @param[in] brandid
# @param[in] country
# @param[in] functionids
#
def level1_multi(cnx, devicetypeid, brandid, country, functionids):
    try:
        excludes = '0'
        lv1_codesets = []
        for each in functionids:
            codesets = level1_each(cnx, devicetypeid, brandid, country, each, excludes)
            lv1_codesets += codesets
        return lv1_codesets

    except Exception, e:
        print 'level1_multi::%s' % e


# \fn level2
# \note
#   !!! query only intend to provide correct logic, not optimized for speed and performance.
#   !!!
#
# @param[in] devicetypeid
# @param[in] brandid
# @param[in] country
# @param[in] selid - function key that user has tested.
# @param[in] selval - the value of the function key that selected by user.
# @param[in] functionid - key to retrieve for tryout.  key chosen by api logic.
#
def level2(cnx, devicetypeid, brandid, country, selid, selval, functionid):
    try:
        # generate a list of qualified codesets.
        query = ("SELECT DISTINCT a.codesetid FROM uesidfunctionmap a "
                 "JOIN uescodes b ON b.uesid = a.uesid "
                 "JOIN codesets c ON c.codesetid = a.codesetid "
                 "WHERE a.activeflag = 'Y' AND c.activeflag = 'Y' "  # only if both codeset and keycode are "active".
                 "AND c.devicetypeid = %d "  # @param[in] devicetypeid
                 "AND c.brandid = %d "  # @param[in] brandid
                 "AND a.functionid = %d "  # @param[in] selid
                 "AND b.encodedbinary = '%s' "  # @param[in] selval
                 % (devicetypeid, brandid, selid, selval))
        cnx.cursor.execute(query)
        rows = cnx.cursor.fetchall()
        codesets = ''
        for each in rows:
            codesets += str(each[0]) + ','
        codesets = codesets[:-1]

        # test if this is a global or localized ranking
        if country is None:
            # use global ranking.
            query = ("SELECT order_by_rank.* FROM "
                     "( "
                     "SELECT a.codesetid, a.uesid, a.functionid, b.encodedbinary, c.rank FROM uesidfunctionmap a "
                     "JOIN uescodes b ON b.uesid = a.uesid "
                     "JOIN codesets c ON c.codesetid = a.codesetid "
                     "WHERE a.codesetid IN (%s) "
                     "AND a.functionid = %d "  # @param[in] functionid
                     "ORDER BY c.rank "  # rank by global.
                     ") AS order_by_rank "
                     "GROUP BY order_by_rank.encodedbinary "  # remove duplicated based on encoded binary value.
                     "ORDER by order_by_rank.rank "
                     % (codesets, functionid))
        else:
            # use localized ranking.
            query = ("SELECT order_by_rank.* FROM "
                     "( "
                     "SELECT a.codesetid, a.uesid, a.functionid, b.encodedbinary, c.rank AS grank, d.rank AS lrank, "
                     "IF(d.rank, d.rank, c.rank+5) AS ranking "  # local ranking promotion.
                     "FROM uesidfunctionmap a "
                     "JOIN uescodes b ON b.uesid = a.uesid "
                     "JOIN codesets c ON c.codesetid = a.codesetid "
                     "LEFT OUTER JOIN countrycodesetmap d ON d.codesetid = a.codesetid "
                     "WHERE a.codesetid IN (%s) "
                     "AND a.functionid = %d "  # @param[in] functionid
                     "ORDER BY ranking "  # rank by promoting local by 5.
                     ") AS order_by_rank "
                     "GROUP BY order_by_rank.encodedbinary "  # remove duplicated based on encoded binary value.
                     "ORDER by order_by_rank.ranking "
                     % (codesets, functionid))

        cnx.cursor.execute(query)
        rows = cnx.cursor.fetchall()
        #if len(rows) > 1:
        print '\nlevel2 (%d=%s) item count: %d' % (selid, selval, len(rows))
        for ea in rows:
            print ea

    except Exception, e:
        print 'level2::%s' % e


def level3(cnx, devicetypeid, brandid, country, selid, selval, selid2, selval2, functionid):
    try:
        # generate a list of qualified codesets.
        query = ("SELECT DISTINCT a.codesetid FROM uesidfunctionmap a "
                 "JOIN uescodes b ON b.uesid = a.uesid "
                 "JOIN codesets c ON c.codesetid = a.codesetid "
                 "WHERE a.activeflag = 'Y' AND c.activeflag = 'Y' "  # only if both codeset and keycode are "active".
                 "AND c.devicetypeid = %d "  # @param[in] devicetypeid
                 "AND c.brandid = %d "  # @param[in] brandid
                 "AND a.functionid = %d "  # @param[in] selid
                 "AND b.encodedbinary = '%s' "  # @param[in] selval
                 % (devicetypeid, brandid, selid, selval))
        cnx.cursor.execute(query)
        rows = cnx.cursor.fetchall()
        codesets = ''
        for each in rows:
            codesets += str(each[0]) + ','
        codesets = codesets[:-1]

        # generate a list of qualified codesets.
        query = ("SELECT DISTINCT a.codesetid FROM uesidfunctionmap a "
                 "JOIN uescodes b ON b.uesid = a.uesid "
                 "JOIN codesets c ON c.codesetid = a.codesetid "
                 "WHERE a.activeflag = 'Y' AND c.activeflag = 'Y' "  # only if both codeset and keycode are "active".
                 "AND c.devicetypeid = %d "  # @param[in] devicetypeid
                 "AND c.brandid = %d "  # @param[in] brandid
                 "AND a.functionid = %d "  # @param[in] selid
                 "AND b.encodedbinary = '%s' "  # @param[in] selval
                 "AND a.codesetid IN (%s) "
                 % (devicetypeid, brandid, selid2, selval2, codesets))
        cnx.cursor.execute(query)
        rows = cnx.cursor.fetchall()
        codesets = ''
        for each in rows:
            codesets += str(each[0]) + ','
        codesets = codesets[:-1]

        # test if this is a global or localized ranking
        if country is None:
            # use global ranking.
            query = ("SELECT order_by_rank.* FROM "
                     "( "
                     "SELECT a.codesetid, a.uesid, a.functionid, b.encodedbinary, c.rank FROM uesidfunctionmap a "
                     "JOIN uescodes b ON b.uesid = a.uesid "
                     "JOIN codesets c ON c.codesetid = a.codesetid "
                     "WHERE a.codesetid IN (%s) "
                     "AND a.functionid = %d "  # @param[in] functionid
                     "ORDER BY c.rank "  # rank by global.
                     ") AS order_by_rank "
                     "GROUP BY order_by_rank.encodedbinary "  # remove duplicated based on encoded binary value.
                     "ORDER by order_by_rank.rank "
                     % (codesets, functionid))
        else:
            # use localized ranking.
            query = ("SELECT order_by_rank.* FROM "
                     "( "
                     "SELECT a.codesetid, a.uesid, a.functionid, b.encodedbinary, c.rank AS grank, d.rank AS lrank, "
                     "IF(d.rank, d.rank, c.rank+5) AS ranking "  # local ranking promotion.
                     "FROM uesidfunctionmap a "
                     "JOIN uescodes b ON b.uesid = a.uesid "
                     "JOIN codesets c ON c.codesetid = a.codesetid "
                     "LEFT OUTER JOIN countrycodesetmap d ON d.codesetid = a.codesetid "
                     "WHERE a.codesetid IN (%s) "
                     "AND a.functionid = %d "  # @param[in] functionid
                     "ORDER BY ranking "  # rank by promoting local by 5.
                     ") AS order_by_rank "
                     "GROUP BY order_by_rank.encodedbinary "  # remove duplicated based on encoded binary value.
                     "ORDER by order_by_rank.ranking "
                     % (codesets, functionid))

        cnx.cursor.execute(query)
        rows = cnx.cursor.fetchall()
        print 'level3 item count: ', len(rows)
        for each in rows:
            print each

    except Exception, e:
        print 'level3::%s' % e


def get_codeset_count(cnx, devicetypeid, brandid):
    try:
        query = ("SELECT codesetid FROM codesets "
                 "WHERE activeflag = 'Y' "
                 "AND devicetypeid = %d "
                 "AND brandid = %d "
                 "GROUP BY codesetid; "
                 % (devicetypeid, brandid))
        cnx.cursor.execute(query)
        rows = cnx.cursor.fetchall()
        return len(rows)
    except Exception, e:
        print 'get_codeset_count::%s' % e


def get_brands(cnx, devicetypeid):
    try:
        query = ("SELECT a.brandid, b.brandname FROM codesets a "
                 "JOIN brands b ON b.brandid = a.brandid "
                 "WHERE a.activeflag = 'Y' "
                 "AND a.devicetypeid = '%d' "
                 "GROUP BY a.brandid; "
                 % devicetypeid)
        cnx.cursor.execute(query)
        return cnx.cursor.fetchall()
    except Exception, e:
        print 'get_brands::%s' % e


def get_devicetypes(cnx):
    try:
        query = ("SELECT a.devicetypeid, b.function_ids_for_level_1, a.devicetype FROM devicetypes a "
                 "JOIN disambiguate_functions b on b.device_type_id = a.devicetypeid "
                 "GROUP BY a.devicetypeid; ")
        cnx.cursor.execute(query)
        return cnx.cursor.fetchall()
    except Exception, e:
        print 'get_devicetypes::%s' % e


def main():
    log = ir.Logger("das")
    log.out.write("devicetypeid|brandid|codesets|distincts|ratio|delta|brandname|devicetype\n")
    cnx = ir.DBConnection()
    #cnx = DBConnection(host='54.254.101.29', user='kai', passwd='p33lz3l')
    try:
        devicetypes = get_devicetypes(cnx)
        for devicetypeid in devicetypes:
            brands = get_brands(cnx, devicetypeid[0])
            #print "\n%d brands." % len(brands)
            for brandid in brands:
                print brandid[1], devicetypeid[2]
                dist = get_level1_count(cnx, devicetypeid[0], brandid[0], devicetypeid[1])
                full = get_codeset_count(cnx, devicetypeid[0], brandid[0])
                log.out.write("%d|%d|%d|%d|%0.2f|%d|%s|%s\n"
                              % (devicetypeid[0],
                                 brandid[0],
                                 full,
                                 dist,
                                 (dist * 100.0) / full,
                                 full - dist,
                                 brandid[1],
                                 devicetypeid[2]))
            log.out.flush()
    except Exception, e:
        print 'main::%s' % e


if __name__ == '__main__':
    main()