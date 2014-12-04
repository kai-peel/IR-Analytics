##  @package acodesets
#   Report code counts on active codesets per device type.
#
from collections import defaultdict
import irutils
#IR_CODE_DATABASE = "54.254.101.29"  # staging
#IR_CODE_DATABASE = "175.41.143.31"  # production

MAXIMUM_DUPLICATES = 3

g_duplicates = []
g_candidates = []


##  @fn
#   @brief
#
def get_functions(cnx, codesetid, dtype):
    tbl = "functions"
    if dtype == 1:
        tbl = "tvfunctions"
    elif dtype == 2:
        tbl = "stbfunctions"
    elif (dtype == 3) or (dtype == 4):
        tbl = "dvdfunctions"
    elif dtype == 5:
        tbl = "avfunctions"
    elif dtype == 10:
        tbl = "prjfunctions"

    query = ("SELECT m.functionid, c.format, c.syscode, c.datacode, c.encodedbinary2, f.functionname "
             "FROM uesidfunctionmap m "
             "JOIN uescodes c ON c.uesid = m.uesid "
             "JOIN functions f ON f.id = m.functionid "
             "WHERE m.activeflag = 'Y' "
             "AND m.codesetid = %d "
             "AND m.functionid IN (SELECT id FROM %s) "
             #"AND m.functionid IN (SELECT id FROM %s WHERE functiongroup='Basic') "
             "ORDER BY m.functionid" % (codesetid, tbl))
    try:
        cnx.cursor.execute(query)
        return cnx.cursor.fetchall()

    except Exception, e:
        print e
        return None


##  @fn
#   @brief
#
def get_function_count(cnx, codesetid, dtype):
    tbl = "functions"
    if dtype == 1:
        tbl = "tvfunctions"
    elif dtype == 2:
        tbl = "stbfunctions"
    elif (dtype == 3) or (dtype == 4):
        tbl = "dvdfunctions"
    elif dtype == 5:
        tbl = "avfunctions"
    elif dtype == 10:
        tbl = "prjfunctions"

    query = ("SELECT uesid FROM uesidfunctionmap  "
             "WHERE activeflag = 'Y' AND codesetid = %d "
             "AND functionid IN (SELECT id FROM %s WHERE functiongroup='Basic') "
             % (codesetid, tbl))
    try:
        cnx.cursor.execute(query)
        cnx.cursor.fetchall()
        return cnx.cursor.rowcount

    except Exception, e:
        print e
        return 0


def get_basic_functions(cnx, dtype):
    tbl = "functions"
    if dtype == 1:
        tbl = "tvfunctions"
    elif dtype == 2:
        tbl = "stbfunctions"
    elif (dtype == 3) or (dtype == 4):
        tbl = "dvdfunctions"
    elif dtype == 5:
        tbl = "avfunctions"
    elif dtype == 10:
        tbl = "prjfunctions"

    query = ("SELECT * FROM %s" % tbl)
    #query = ("SELECT * FROM %s WHERE functiongroup = 'Basic'" % tbl)
    try:
        cnx.cursor.execute(query)
        return cnx.cursor.fetchall()

    except Exception, e:
        print e
        return None


##  @fn
#   @brief compare tv's functions between codeset1 and codeset2
#       codeset1 assume to be higher (top) ranked than codeset2
#
def compare_codesets(log, cnx, dtype, codesetid1, func1, codesetid2, brandname):
    global g_duplicates
    global g_candidates

    func2 = get_functions(cnx, codesetid2, dtype)

    diff = []  # key code is different.
    miss = []  # key does not exist in top codeset
    na = []  # no code values to compare (either of the codeset)
    dup = []  # identical (duplicated)

    # top ranking (func1) should be the super set.
    #print func1.items()
    for k, f, s, d, v, n in func2:
        try:
            if not v:
                na.append(n)
            elif not func1[k]:
                miss.append(n)
            else:
                # compare if there's decoded system code and data code, compare format, system code and data code.
                if func1[k][1] > 0 or func1[k][2] > 0:
                    if func1[k][0] == f and func1[k][1] == s and func1[k][2] == d:
                        dup.append(n)
                    else:
                        diff.append(n)
                # if no decoded value (most of the a/c cases), use full code to compare.
                elif func1[k][3] == v:
                    dup.append(n)
                else:
                    diff.append(n)

        except Exception, e:
            print e

    if len(dup) > 0 and len(diff) < 1:
        # mark as duplicate if
        # 1) no difference
        # 2) higher ranked codeset need to be "supersized" than lower ranked codeset. (no missing key)
        if len(miss) < 1 and len(na) < 1:
            g_duplicates.append(codesetid2)
            log.log.write("%s|%d|%d|%d\n" % (brandname, dtype, codesetid2, codesetid1))
        else:
            # mark as candidate because no analyzed data to compare keys.
            g_candidates.append(codesetid2)
            log.log.write("%s|%d|%d||%d|%s|%s\n" % (brandname, dtype, codesetid2, codesetid1, miss, na))

    log.log.flush()
    #log.err.flush()


##  @fn
#   @brief get list of active codesets by brandid and devicetypeid
#
def get_codesets_by_brand(log, cnx, dtype, brandid, brandname):
    global g_duplicates
    global g_candidates
    g_duplicates = []
    g_candidates = []

    query = ("SELECT DISTINCT codesetid FROM codesets "
             "WHERE brandid=%d AND devicetypeid=%d AND activeflag='Y' "
             "ORDER BY rank" % (brandid, dtype))
    try:
        cnx.cursor.execute(query)
        codesets = cnx.cursor.fetchall()
        #log.err.write("%s|%d|%d|" % (brandname, dtype, cnx.cursor.rowcount))
        if cnx.cursor.rowcount > 1:
            rowcount = cnx.cursor.rowcount

            for i in range(rowcount):
                # check only if the codeset has not been marked as 'duplicate'.
                if codesets[i][0] not in (g_duplicates + g_candidates):
                    s = get_functions(cnx, codesets[i][0], dtype)
                    func1 = defaultdict(str)

                    for k, f, s, d, v, n in s:
                        func1[k] = [f, s, d, v, n]

                    log.log.write("%s|%d|%d\n" % (brandname, dtype, codesets[i][0]))

                    for j in range(i+1, rowcount):
                        # check only if the codeset has not been marked as 'duplicate'.
                        if codesets[j][0] not in (g_duplicates + g_candidates):
                            print "+- top(%d) compare with codesets(%d)." % (codesets[i][0], codesets[j][0])
                            compare_codesets(log, cnx, dtype, codesets[i][0], func1, codesets[j][0], brandname)

        #log.err.write("%d|%d\n" % (len(g_duplicates), len(g_candidates)))

    except Exception, e:
        print e


##  @fn
#   @brief get list of active codesets by devicetypeid and check how many keys in the codeset.
#
def get_codesets_by_devicetype(log, cnx, dtype):
    query = ("SELECT DISTINCT codesetid FROM codesets "
             "WHERE devicetypeid=%d AND activeflag='Y' " % dtype)
    try:
        cnx.cursor.execute(query)
        codesets = cnx.cursor.fetchall()
        for i in range(cnx.cursor.rowcount):
            cnt = get_function_count(cnx, codesets[i][0], dtype)
            log.log.write("%d|%d\n" % (codesets[i][0], cnt))
            log.log.flush()
    except Exception, e:
        print e


def get_key_by_brand(log, cnx, dtype, brandid, funcid):
    query = ("SELECT f.uesid FROM uesidfunctionmap f "
             "JOIN codesets s ON s.codesetid = f.codesetid "
             "WHERE s.activeflag = 'Y' AND f.activeflag = 'Y' "
             "AND s.brandid = %d AND s.devicetypeid = %d AND f.functionid = %d "
             % (brandid, dtype, funcid))

    cnx.cursor.execute(query)
    rows = cnx.cursor.fetchall()
    total = len(rows)

    query = ("SELECT COUNT(*) FROM uescodes c "
             "JOIN uesidfunctionmap f ON f.uesid = c.uesid "
             "JOIN codesets s ON s.codesetid = f.codesetid "
             "WHERE s.activeflag = 'Y' AND f.activeflag = 'Y' "
             "AND s.brandid = %d AND s.devicetypeid = %d AND f.functionid = %d "
             "GROUP BY c.encodedbinary "
             % (brandid, dtype, funcid))

    cnx.cursor.execute(query)
    rows = cnx.cursor.fetchall()
    unique = len(rows)
    dup = sum(t[0] for t in rows) - unique

    return total, unique, dup


def get_keys_by_brand(log, cnx, dtype, brandid, brandname):
    #print("checking brandid = %d" % brandid)
    rpt = Logger("%d-%s-%d" % (brandid, brandname, dtype))
    rpt.log.write("%s|%s|%s|%s|%s\n" % ("Function Name", "Total", "Unique", "Duplicate", "Unknown"))

    func = get_basic_functions(cnx, dtype)
    try:
        for key in func:
            total, unique, dup = get_key_by_brand(log, cnx, dtype, brandid, key[0])
            rpt.log.write("%s|%d|%d|%d|%d\n" % (key[1], total, unique, dup, total - unique - dup))

        rpt.log.flush()

    except Exception, e:
        print e


##  @fn
#   @brief get list of brands by devicetypeid
#
def get_brands(log, cnx, dtype):
    query = ("SELECT DISTINCT m.brandid, brandname from brandtypemap m "
             "JOIN brands b ON b.brandid=m.brandid "
             "WHERE devicetypeid=%d "
             "ORDER BY rank "
             #"LIMIT 10"
             % dtype)
    try:
        cnx.cursor.execute(query)
        brands = cnx.cursor.fetchall()
        for row in brands:
            print("checking brandid = %d" % row[0])
            get_codesets_by_brand(log, cnx, dtype, row[0], row[1])

    except Exception, e:
        print e


def get_brands_by_codesets_count(log, cnx, dtype):
    query = ("SELECT DISTINCT b.brandid, b.brandname, COUNT(*) as cnt from codesets s "
             "JOIN brands b ON b.brandid=s.brandid "
             "WHERE s.devicetypeid=%d "
             "AND s.activeflag='Y' "
             "GROUP BY s.brandid "
             #"HAVING cnt > 10 "
             "ORDER BY cnt DESC "
             "LIMIT 3 "
             % dtype)
    try:
        cnx.cursor.execute(query)
        brands = cnx.cursor.fetchall()
        for row in brands:
            print("checking brandid = %d" % row[0])
            get_keys_by_brand(log, cnx, dtype, row[0], row[1])
            get_codesets_by_brand(log, cnx, dtype, row[0], row[1])

    except Exception, e:
        print e


def main():
    log = irutils.Logger("cset")
    cnx = irutils.DBConnection()

    log.log.write("%s|%s\n" % ("Codeset", "Keys"))

    get_codesets_by_devicetype(log, cnx, 10)


if __name__ == '__main__':
    main()
