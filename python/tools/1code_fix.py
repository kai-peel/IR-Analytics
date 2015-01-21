from utils import irutils as ir
UESID = 124473
FREQ = 37000
PULSES = [11,67,11,27,11,27,11,27,11,67,11,67,11,27,11,27,11,67,11,27,11,67,11,27,11,27,11,67,11,27,11,1678,11,67,11,27,11,27,11,27,11,67,11,27,11,67,11,67,11,27,11,67,11,27,11,67,11,67,11,27,11,67,11,1600]


def delete_uespulses(cnx, id):
    query = ("DELETE FROM uespulses "
             "WHERE uesid = %d; "
             % id)
    try:
        cnx.cursor.execute(query)
        cnx.db.commit()
    except Exception, e:
        print e


def insert_uespulses(cnx, id, pulses):
    for x in xrange(len(pulses)):
        query = ("INSERT INTO uespulses(uesid, seq, pulse, frame) "
                 "VALUE(%d, %d, %d, 'M'); "
                 % (id, x, pulses[x]))
        try:
            cnx.cursor.execute(query)
        except Exception, e:
            print e

    cnx.db.commit()


def main():
    cnx = ir.DBConnection()
    delete_uespulses(cnx, UESID)
    insert_uespulses(cnx, UESID, PULSES)

if __name__ == '__main__':
    main()
