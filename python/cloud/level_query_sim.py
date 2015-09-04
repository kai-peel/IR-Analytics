#!/usr/bin/python
__author__ = 'kai'
__version__ = '3.0'
__date__ = '29-Jul-2015'
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
def level1(cnx, devicetypeid, brandid, country, functionid):
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
        rows = cnx.cursor.fetchall()
        print len(rows)
        for each in rows:
            print each

    except Exception, e:
        print 'level1::%s' % e


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
        print '\nitem count: ', len(rows)
        for each in rows:
            print each
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
        level1 = []
        for each in functionids:
            codesets = level1_each(cnx, devicetypeid, brandid, country, each, excludes)
            level1 += codesets
        return level1

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


if __name__ == '__main__':
    cnx = DBConnection()
    #cnx = DBConnection(host='54.254.101.29', user='kai', passwd='p33lz3l')

    brands = [17] #, 87, 64, 74, 23, 30, 37, 69, 32, 57, 31, 36, 80, 24, 179, 41, 86, 165, 76, 197, 196, 283, 75, 38, 169, 78, 46, 82, 580, 172, 22, 222, 176, 200, 207, 166, 244, 560, 77, 7, 193, 173, 175, 25, 224, 148, 182, 72, 243, 185, 167, 187, 168, 251, 572, 50, 84, 139, 273, 27, 178, 230, 66, 163, 678, 1856, 164, 208, 302, 184, 2071, 304, 211, 246, 188, 39, 213, 255, 561, 192, 79, 171, 258, 20, 195, 267, 270, 619, 58, 177, 324, 625, 1832, 206, 419, 642, 1849, 238, 293, 490, 240, 507, 703, 1942, 209, 303, 528, 773, 210, 532, 777, 2519, 305, 545, 1183, 2551, 4, 212, 306, 1313, 2556, 6, 191, 307, 1323, 2559, 170, 217, 257, 309, 571, 1327, 2645, 9, 218, 311, 1337, 2647, 11, 44, 194, 219, 264, 312, 576, 1505, 220, 313, 577, 1596, 174, 221, 269, 314, 1747, 56, 315, 584, 1782, 198, 223, 271, 321, 1828]
    for brandid in brands:
        print '\n', brandid
        # 1st Level:
        # http://ec2-54-251-11-99.ap-southeast-1.compute.amazonaws.com:8080/targets/v2/disambiguate?devicetypeid=1&brandid=45&qstring=&country=CN&userid=821390208&tid=9560cb7161b9ca340b9e0279a5c4d9a3ba0ccffd
        # authorization: Peel c583c7c46eef455992a6846c81573f02:loO0ZUR7N9VsEeGr5mFWHIsOZNo=
        #
        # function (power) chosen by api logic.
        #level1(cnx, 2, 37, 'CN', 15)  # check for power only, china localized.
        #level1(cnx, 5, 42, None, 23)  # check for power only, global.

        # function (power) chosen by api logic.
        #level1(cnx, 5, 45, 'CN', 23)  # check for power only, china localized.
        level1 = level1_multi(cnx, 18, brandid, None, [23, 332])  # check for both power and poweron, global.

        # These are the functions verifying in disambiguate api response for level2 and above
        # if devicetypeid=1 then functions to assert is any one in this list
        # {27,12,13,14}

        # 2nd level:
        # http://ec2-54-251-11-99.ap-southeast-1.compute.amazonaws.com:8080/targets/v2/disambiguate?devicetypeid=1&brandid=45&qstring=23_111100101010000011010101xF2A0D5x&country=CN&userid=821390208&tid=9560cb7161b9ca340b9e0279a5c4d9a3ba0ccffd
        # authorization: Peel c583c7c46eef455992a6846c81573f02:loO0ZUR7N9VsEeGr5mFWHIsOZNo=
        # functionid chosen by api logic.
#        for each in level1:
#            level2(cnx, 1, brandid, 'CN', each[2], each[3], 13)  # check for power only, china localized.
        #level2(cnx, 1, 45, None, 23, '111100101010000011010101xF2A0D5x', 27)  # check for power only, global.
        #level2(cnx, 1, 254, 'CN', 23, '11000000001100x000Cx', 27)
        #level3(cnx, 1, 254, 'CN', 23, '11000000001100x000Cx', 27, '11000000101110x002Ex', 13)
        #level3(cnx, 1, 254, 'CN', 23, '00BF0DF2', 27, '00BF14EB', 13)
