__author__ = 'kai'
__version__ = '1.0'
__date__ = '30-Dec-2014'
from utils import irutils


def main():
    log = irutils.Logger('csv')
    cnx = irutils.DBConnection('127.0.0.1', 'test')

    try:
        query = 'SHOW columns from india '
        cnx.cursor.execute(query)
        _cols = cnx.cursor.fetchall()
        cols = []
        for col in _cols:
            cols.append(col[0])
        print cols

        query = "SELECT * from india "
        cnx.cursor.execute(query)
        csets = cnx.cursor.fetchall()
        for cset in csets:
            n = cset[0]
            for x in xrange(1, len(cset)):
                if cset[x] is not None and len(cset[x]):
                    ln = '%s||Full_Repeat|%s|%s|\n' % (n, cols[x], cset[x])
                    log.log.write(ln)
        log.log.flush()

    except Exception, e:
        print e


if __name__ == '__main__':
    main()