__version__ = "1.0.0"
__date__ = "05-DEC-2014"
import numpy as np
from utils import irutils
from utils import irhist as ph
#DBTOCONNECT="175.41.143.31"  # production
DBTOCONNECT = "54.254.101.29"  # staging
DBTABLE = "user_ir_capture_"
DBTBCNT = 20


def csv2array(csv, delimiter):
    r = []
    a = csv.split(delimiter)
    for each in a:
        r.append(int(each))
    return r


def make_hashcode(log, frequency, frame):
    ps = ph.BurstPairs(frame)
    return ps


def main(part):
    log = irutils.Logger("hc")
    cnx = irutils.DBConnection(DBTOCONNECT, "kai")
    table = "%s%s" % (DBTABLE, part[0])
    print "checking `%s`..." % table
    query = ("SELECT uicid, frequency, frame FROM %s "
             "WHERE frame IS NOT NULL and frame != 'None' "
             "AND frequency IS NOT NULL and frequency != 'None' "
             "and hashcode IS NULL"
             % table)
    try:
        cnx.cursor.execute(query)
        captures = cnx.cursor.fetchall()
        for idx, frequency, frame in captures:
            try:
                code = make_hashcode(log, frequency, frame)
            except Exception, e:
                print "ERR:ID(%d): %s." % (idx, e)
    except Exception, e:
        print e

TESTFRAME='96 30 17 30 17 16 17 16 17 30 32 15 17 16 17 16 17 16 17 16 17 16 17 16 17 16 17 16 17 16 17 16 17 16 32 15 17 30 17 16 17 3053'
#TESTFRAME='8 35 8 67 8 29 8 110 8 51 8 51 8 45 8 104 8 499 8 35 8 67 8 29 8 29 8 29 8 72 8 29 8 29 8 3141 8 35 8 67 8 29 8 110 8 51 8 51 8 45 8 104 8 499 8 35 8 110 8 72 8 29 8 29 8 72 8 29 8 29 8 3141 8 35 8 67 8 29 8 110 8 51 8 51 8 45 8 104 8 499 8 35 8 110 8 72 8 29 8 29 8 72 8 29 8 29 8 780'

if __name__ == '__main__':
    #main(sys.argv[1:])
    log = irutils.Logger("hc")
    frame = csv2array(TESTFRAME, ' ')
    make_hashcode(log, 38000, frame)