__version__ = "3.0.0"
__date__ = "25-MAR-2015"
#import MySQLdb
#import time
#IR_CODE_DATABASE = "175.41.143.31"  # production
from utils import irutils as ir
#FAN_SPEED = ['A', '1', '2', '3']
#OP_MODE = ['H', 'C']


def mv_P_to_PO(cnx, codesetid):
    src = 23  # 'Power'
    dest = 332  # 'PowerOn'
    query = ("SELECT * from uesidfunctionmap "
             "WHERE functionid = %d AND activeflag = 'Y' "
             "AND codesetid = %d " % (src, codesetid))
    #print query
    try:
        cnx.cursor.execute(query)
        uescodes = cnx.cursor.fetchall()
        if cnx.cursor.rowcount > 0:
            uescode = uescodes[0]
            query = ("UPDATE uesidfunctionmap "
                     "SET functionid = %d "
                     "WHERE uesid = %d AND codesetid = %d AND functionid = %d "
                     % (dest, uescode[0], uescode[1], uescode[2]))
            #print query
            try:
                cnx.cursor.execute(query)
            except Exception, e:
                print e
            return uescode[0]
        else:
            return -1
    except Exception, e:
        print e


def copy_uesidfunc(cnx, codesetid, dest, src):
    #src = 6216  # '26_F_A_C=6216'
    #dest = 332  # 'PowerOn'
    query = ("INSERT INTO uesidfunctionmap (uesid, codesetid, functionid, origfunctionid, updateddate, activeflag) "
             "SELECT uesid, codesetid, %d, origfunctionid, updateddate, activeflag "
             "FROM uesidfunctionmap "
             "WHERE activeflag = 'Y' AND codesetid = %d "
             "AND functionid = %d " % (dest, codesetid, src))
    #print query
    try:
        cnx.cursor.execute(query)
    except Exception, e:
        print e


def main():
    log = ir.Logger("pwr")
    cnx = ir.DBConnection()

    # find a/c codes id as "brute force" 26_F_A_C=6216, but no associated a/c code PowerOn=332.
    query = ("SELECT DISTINCT m.codesetid from uesidfunctionmap m "
             "JOIN codesets s ON s.codesetid = m.codesetid "
             "WHERE m.functionid = 6216 "
             "AND m.activeflag='Y' AND s.activeflag = 'Y' "
             "AND m.codesetid NOT IN "
             "(SELECT DISTINCT codesetid FROM uesidfunctionmap "
             "WHERE functionid = 332 AND activeflag = 'Y') ")
    try:
        cnx.cursor.execute(query)
        codesets = cnx.cursor.fetchall()
        for codesetid in codesets:
            log.write("processing codesetid %d..." % codesetid[0])
            uesid = mv_P_to_PO(cnx, codesetid[0])
            if uesid < 0:
                copy_uesidfunc(cnx, codesetid[0], 332, 6216)
        cnx.db.commit()
    except Exception, e:
        print e


if __name__ == '__main__':
    main()
