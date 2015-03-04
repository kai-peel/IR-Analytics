__version__ = "2.0.0"
__date__ = "15-DEC-2014"
#import MySQLdb
#import time
#IR_CODE_DATABASE = "175.41.143.31"  # production
from utils import irutils as ir
FAN_SPEED = ['A', '1', '2', '3']
OP_MODE = ['H', 'C']


def dup_P_to_PO(cnx, codesetid):
                src = 'Power'
                dest = 'PowerOn'
                query = ("SELECT * from uesidfunctionmap m "
                         "JOIN functions f ON f.id = m.functionid "
                         "WHERE f.functionname = '%s' AND m.activeflag = 'Y' "
                         "AND m.codesetid = %d " % (src, codesetid))
                #print query
                try:
                    cnx.cursor.execute(query)
                    uescodes = cnx.cursor.fetchall()
                    if cnx.cursor.rowcount > 0:
                        uescode = uescodes[0]
                        query = ("SELECT id from functions "
                                 "WHERE functionname = '%s' " % dest)
                        #print query
                        try:
                            cnx.cursor.execute(query)
                            funcs = cnx.cursor.fetchall()
                            if cnx.cursor.rowcount > 0:
                                func = funcs[0][0]
                                query = ("INSERT INTO uesidfunctionmap (uesid, codesetid, functionid, origfunctionid, updateddate, activeflag) "
                                         "SELECT uesid, codesetid, %d, origfunctionid, updateddate, activeflag "
                                         "FROM uesidfunctionmap "
                                         "WHERE uesid = %d "
                                         "AND codesetid = %d "
                                         "AND functionid = %d " % (func, uescode[0], uescode[1], uescode[2]))
                                #print query
                                try:
                                    cnx.cursor.execute(query)
                                    cnx.db.commit()
                                except Exception, e:
                                    print e
                        except Exception, e:
                            print e
                except Exception, e:
                    print e


def main():
    log = ir.Logger("f2s")
    cnx = ir.DBConnection()

    # find a/c codes id as "brute force" 20_F_A_C=6210, but no associated a/c code PowerOn=332.
    query = ("SELECT DISTINCT m.codesetid from uesidfunctionmap m "
             "JOIN codesets s ON s.codesetid = m.codesetid "
             "WHERE m.functionid = 6210 "
             "AND m.activeflag='Y' AND s.activeflag = 'Y' "
             "AND m.codesetid NOT IN "
             "(SELECT DISTINCT codesetid FROM uesidfunctionmap "
             "WHERE functionid = 332 AND activeflag = 'Y') ")
    try:
        cnx.cursor.execute(query)
        codesets = cnx.cursor.fetchall()
        for codesetid in codesets:
            log.write("processing codesetid %d..." % codesetid[0])
            dup_P_to_PO(cnx, codesetid[0])
    except Exception, e:
        print e


if __name__ == '__main__':
    main()
