#!/usr/bin/python
__author__ = 'kai'
__version__ = '3.0'
__date__ = '29-Jul-2015'
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
        return len(rows)

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
    cnx = ir.DBConnection()
    #cnx = DBConnection(host='54.254.101.29', user='kai', passwd='p33lz3l')
    f = ir.Logger('disam', 1)

    brands = [37, 30, 231, 194, 1356, 584, 31, 120, 253, 422, 32, 128, 1362, 123, 42, 603, 23, 419, 41, 20, 430, 2116, 711, 563, 1361, 134, 1366, 809, 490, 439, 1338, 604, 36, 914, 1364, 46, 761, 67, 203, 935, 260, 681, 1735, 781, 2588, 2589, 139, 1037, 121, 602, 979, 528, 1678, 254, 901, 1363, 1685, 756, 1324, 1752, 921, 683, 788, 2609, 1758, 1357, 1944, 844, 2583, 798, 574, 1033, 259, 677, 358, 359, 268, 1757, 27, 232, 233, 385, 843, 2166, 755, 758, 802, 1688, 24, 125, 2683, 1225, 2738, 842, 2581, 368, 747, 1396, 1505, 1595, 1702, 814, 948, 671, 2586, 17, 204, 883, 1454, 136, 902, 438, 757, 2132, 837, 122, 838, 854, 474, 1472, 2150, 1219, 2733, 481, 1393, 280, 2582, 812, 946, 1945, 1442, 1048, 949, 39, 917, 256, 641, 851, 2105, 2133, 45, 643, 1755, 2657, 25, 1527, 361, 1713, 475, 942, 1477, 559, 1672, 2113, 793, 876, 1485, 1673, 3, 811, 895, 1376, 1490, 1536, 669, 796, 1047, 1360, 1397, 2195, 1049, 412, 540, 1317, 1706, 1517, 545, 657, 785, 834, 1101, 1365, 1406, 118, 376, 1408, 1816, 2034, 2171, 852, 1003, 2704, 265, 939, 1524, 1820, 2173, 230, 360, 2595, 558, 700, 808, 1372, 1865, 2531, 126, 278, 365, 648, 857, 875, 910, 858, 1394, 2739, 235, 667, 1395, 1577, 1718, 2192, 2446, 2615, 130, 564, 2018, 568, 751, 879, 947, 1013, 1029, 1742, 371, 830, 915, 1381, 1549, 15, 38, 571, 654, 815, 831, 881, 998, 1550, 2167, 86, 328, 432, 848, 983, 2027, 2587, 374, 784, 1554, 117, 867, 1035, 1457, 1518, 986, 1386, 2590, 228, 1332, 149, 870, 906, 988, 1135, 1668, 2592, 150, 379, 662, 806, 1370, 1471, 1563, 2109, 2561, 2626, 2658, 153, 990, 1371, 1694, 52, 382, 599, 647, 664, 769, 791, 840, 958, 1042, 1091, 1340, 1392, 1530, 1565, 2153, 2176, 2216, 57, 174, 383, 665, 770, 792, 841, 992, 1430, 1531, 1737, 2073, 2156, 2177, 2217, 2533, 2613, 2629, 127, 406, 649, 666, 1227, 1738, 1831, 2115, 2191, 2685, 2824, 425, 794, 877, 994, 1027, 1094, 1700, 2080, 2537, 2599, 2686, 183, 304, 369, 386, 428, 779, 878, 1095, 1359, 1701, 1719, 2447, 2600, 2853, 321, 780, 1063, 1079, 1096, 1510, 1537, 1676, 1804, 2633, 69, 199, 249, 322, 388, 410, 610, 670, 797, 965, 1030, 1064, 1097, 1513, 1721, 1964, 2097, 2126, 2764, 431, 900, 933, 966, 1081, 1452, 1514, 2127, 864, 967, 1082, 1403, 2099, 2604, 2808, 543, 673, 800, 817, 833, 865, 968, 1000, 1034, 1456, 1686, 1726, 2169, 2809, 21, 226, 582, 1018, 1068, 1119, 1385, 1558, 1687, 1814, 1921, 2102, 2554, 22, 138, 819, 904, 953, 970, 1036, 1120, 1467, 1521, 1560, 1730, 2623, 397, 759, 905, 954, 1522, 1561, 1690, 1710, 2557, 2591, 229, 399, 805, 972, 1038, 1088, 1388, 1470, 1691, 1711, 1785, 2202, 2625, 2819, 468, 645, 923, 989, 1005, 1072, 1106, 1197, 1412, 1692, 2524, 2610, 2706, 2731, 380, 595, 646, 768, 807, 839, 891, 908, 1422, 1529, 1564, 2562, 2682, 2732, 157, 276, 363, 404, 421, 824, 856, 873, 892, 909, 926, 975, 991, 1007, 1024, 1058, 1074, 1109, 1429, 1671, 1696, 1714, 1736, 1761, 1791, 1827, 1895, 1933, 2011, 2057, 2112, 2578, 2596, 2612, 2628, 2660, 2708, 2754, 2774, 2822, 2843, 405, 701, 825, 893, 927, 943, 959, 976, 1009, 1025, 1043, 1059, 1075, 1092, 1110, 1374, 1481, 1566, 1697, 1715, 1762, 1793, 1830, 1866, 1896, 1934, 2012, 2579, 2597, 2661, 2684, 2709, 2755, 2775, 2823, 2844, 58, 175, 234, 367, 384, 424, 484, 562, 702, 771, 810, 826, 894, 911, 928, 944, 961, 977, 993, 1010, 1026, 1044, 1060, 1076, 1093, 1111, 1375, 1431, 1533, 1568, 1698, 1716, 1763, 1797, 1867, 1897, 1938, 2016, 2074, 2157, 2258, 2535, 2598, 2614, 2630, 2662, 2710, 2756, 2776, 2851, 63, 179, 285, 407, 489, 650, 774, 827, 859, 912, 929, 945, 962, 978, 1011, 1045, 1061, 1077, 1112, 1237, 1358, 1434, 1535, 1674, 1739, 1764, 1799, 1833, 1873, 1900, 2017, 2158, 2631, 2663, 2711, 2741, 2757, 2777, 2825, 2852, 7, 33, 237, 408, 608, 651, 668, 795, 828, 860, 896, 913, 930, 963, 995, 1012, 1028, 1046, 1062, 1078, 1113, 1285, 1377, 1436, 1593, 1675, 1740, 1766, 1803, 1837, 1874, 1901, 2082, 2118, 2159, 2193, 2538, 2616, 2632, 2664, 2687, 2712, 2742, 2758, 2798, 2828, 10, 68, 131, 248, 370, 387, 409, 429, 523, 609, 652, 813, 829, 845, 861, 897, 931, 964, 980, 996, 1114, 1314, 1380, 1720, 1771, 1838, 1876, 1904, 1952, 2019, 2084, 2119, 2164, 2194, 2448, 2539, 2584, 2601, 2617, 2670, 2690, 2714, 2743, 2759, 2799, 2829, 13, 133, 525, 569, 653, 752, 846, 862, 880, 898, 932, 981, 997, 1014, 1080, 1115, 1315, 1399, 1446, 1661, 1677, 1703, 1744, 1773, 1805, 1841, 1878, 1905, 2024, 2449, 2540, 2585, 2602, 2618, 2639, 2671, 2692, 2715, 2744, 2800, 2830, 76, 323, 372, 390, 411, 611, 754, 782, 847, 863, 916, 982, 1015, 1032, 1065, 1098, 1116, 1316, 1382, 1400, 1662, 1705, 1722, 1747, 1774, 1806, 1845, 1879, 1906, 1970, 2025, 2098, 2196, 2451, 2543, 2603, 2619, 2642, 2672, 2693, 2716, 2745, 2765, 2805, 2831, 135, 373, 391, 622, 655, 672, 783, 799, 816, 832, 934, 950, 999, 1016, 1050, 1066, 1099, 1117, 1383, 1515, 1551, 1663, 1723, 1748, 1778, 1810, 1846, 1880, 1913, 1982, 2128, 2168, 2197, 2452, 2552, 2620, 2644, 2673, 2694, 2717, 2746, 2766, 2832, 87, 215, 336, 393, 413, 433, 575, 629, 656, 849, 884, 918, 951, 984, 1017, 1051, 1067, 1083, 1100, 1118, 1384, 1404, 1664, 1707, 1779, 1811, 1848, 1882, 1918, 1985, 2028, 2100, 2131, 2198, 2453, 2553, 2605, 2621, 2648, 2674, 2695, 2718, 2747, 2767, 2833, 137, 343, 375, 394, 415, 631, 675, 801, 818, 850, 885, 903, 919, 936, 952, 969, 985, 1001, 1052, 1084, 1325, 1665, 1708, 1728, 1753, 1780, 1853, 1883, 1993, 2029, 2170, 2199, 2455, 2606, 2622, 2654, 2675, 2698, 2719, 2748, 2768, 2815, 2837, 44, 227, 356, 395, 416, 546, 658, 786, 835, 868, 886, 920, 937, 1002, 1019, 1053, 1069, 1086, 1103, 1330, 1666, 1709, 1754, 1781, 1854, 1884, 1923, 1994, 2200, 2456, 2555, 2607, 2655, 2677, 2703, 2720, 2749, 2769, 2817, 2838, 263, 377, 417, 448, 547, 589, 659, 787, 804, 820, 836, 869, 887, 938, 971, 987, 1020, 1054, 1070, 1087, 1104, 1121, 1367, 1387, 1410, 1469, 1667, 1732, 1783, 1819, 1855, 1885, 1924, 1997, 2037, 2106, 2135, 2172, 2201, 2520, 2608, 2624, 2656, 2678, 2721, 2750, 2770, 2818, 2839, 378, 418, 460, 548, 590, 644, 660, 821, 853, 888, 922, 955, 1004, 1021, 1055, 1071, 1105, 1333, 1368, 1411, 1562, 1733, 1756, 1857, 1886, 1930, 2005, 2038, 2107, 2136, 2521, 2560, 2679, 2705, 2730, 2751, 2771, 2840, 47, 400, 549, 592, 697, 762, 789, 822, 871, 889, 907, 940, 956, 973, 1022, 1039, 1056, 1089, 1390, 1669, 1712, 1734, 1788, 1822, 1862, 1889, 1931, 2009, 2039, 2137, 2174, 2208, 2593, 2681, 2752, 2772, 2820, 2841, 26, 50, 272, 402, 420, 554, 663, 699, 790, 823, 855, 872, 925, 941, 957, 974, 1006, 1023, 1041, 1057, 1073, 1090, 1107, 1198, 1339, 1391, 1670, 1790, 1823, 1864, 1894, 1932, 2010, 2054, 2110, 2175, 2212, 2529, 2611, 2627, 2659, 2707, 2753, 2773, 2821, 2842]
    # [1945] #, 87, 64, 74, 23, 30, 37, 69, 32, 57, 31, 36, 80, 24, 179, 41, 86, 165, 76, 197, 196, 283, 75, 38, 169, 78, 46, 82, 580, 172, 22, 222, 176, 200, 207, 166, 244, 560, 77, 7, 193, 173, 175, 25, 224, 148, 182, 72, 243, 185, 167, 187, 168, 251, 572, 50, 84, 139, 273, 27, 178, 230, 66, 163, 678, 1856, 164, 208, 302, 184, 2071, 304, 211, 246, 188, 39, 213, 255, 561, 192, 79, 171, 258, 20, 195, 267, 270, 619, 58, 177, 324, 625, 1832, 206, 419, 642, 1849, 238, 293, 490, 240, 507, 703, 1942, 209, 303, 528, 773, 210, 532, 777, 2519, 305, 545, 1183, 2551, 4, 212, 306, 1313, 2556, 6, 191, 307, 1323, 2559, 170, 217, 257, 309, 571, 1327, 2645, 9, 218, 311, 1337, 2647, 11, 44, 194, 219, 264, 312, 576, 1505, 220, 313, 577, 1596, 174, 221, 269, 314, 1747, 56, 315, 584, 1782, 198, 223, 271, 321, 1828]
    for brandid in brands:
        print '\n', brandid
        # 1st Level:
        # http://ec2-54-251-11-99.ap-southeast-1.compute.amazonaws.com:8080/targets/v2/disambiguate?devicetypeid=1&brandid=45&qstring=&country=CN&userid=821390208&tid=9560cb7161b9ca340b9e0279a5c4d9a3ba0ccffd
        # authorization: Peel c583c7c46eef455992a6846c81573f02:loO0ZUR7N9VsEeGr5mFWHIsOZNo=
        #
        # function (power) chosen by api logic.
        #level1(cnx, 2, 37, 'CN', 15)  # check for power only, china localized.
        #level1(cnx, 5, 42, None, 23)  # check for power only, global.
        #level1(cnx, 3, brandid, None, 23)  # check for power only, global.

        # function (power) chosen by api logic.
        #level1(cnx, 5, 45, 'CN', 23)  # check for power only, china localized.
        level1 = level1_multi(cnx, 2, brandid, 'CN', [15])  # check for both power and poweron, global.

        # These are the functions verifying in disambiguate api response for level2 and above
        # if devicetypeid=1 then functions to assert is any one in this list
        # {27,12,13,14}

        # 2nd level:
        # http://ec2-54-251-11-99.ap-southeast-1.compute.amazonaws.com:8080/targets/v2/disambiguate?devicetypeid=1&brandid=45&qstring=23_111100101010000011010101xF2A0D5x&country=CN&userid=821390208&tid=9560cb7161b9ca340b9e0279a5c4d9a3ba0ccffd
        # authorization: Peel c583c7c46eef455992a6846c81573f02:loO0ZUR7N9VsEeGr5mFWHIsOZNo=
        # functionid chosen by api logic.
        for each in level1:
            sz = level2(cnx, 2, brandid, 'CN', each[2], each[3], 34)  # check for power only, china localized.
            if sz > 1:
                f.logs[0].write('%d, %d, %s.\n' % (brandid, each[2], each[3]))
        #level2(cnx, 1, 45, None, 23, '111100101010000011010101xF2A0D5x', 27)  # check for power only, global.
        #level2(cnx, 1, 254, 'CN', 23, '11000000001100x000Cx', 27)
        #level3(cnx, 1, 254, 'CN', 23, '11000000001100x000Cx', 27, '11000000101110x002Ex', 13)
        #level3(cnx, 1, 254, 'CN', 23, '00BF0DF2', 27, '00BF14EB', 13)
