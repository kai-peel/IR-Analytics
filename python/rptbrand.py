#!/usr/bin/python
__author__ = 'kai'
import os
from utils import irutils

LOGFILE = 'C:/Users/G50/Dropbox/Public/list_of_brands_and_codeset_count.csv'


def report(cnx, log):
    try:
        query = ('SELECT c.devicetype, b.brandname, count(*) '
                 'FROM codesets a, brands b, devicetypes c '
                 'WHERE a.brandid=b.brandid '
                 'AND a.devicetypeid=c.devicetypeid AND a.activeflag="Y" '
                 'GROUP BY a.devicetypeid, a.brandid;')
        cnx.cursor.execute(query)
        r = cnx.cursor.fetchall()
        for each in r:
            log.write('%s,%s,%d\n' % (each[0], each[1], each[2]))

    except Exception, e:
        print 'report: %s' % e


def list_codesets_per_brand_type():
    try:
        os.remove(LOGFILE)
    except OSError:
        pass
    with open(LOGFILE, 'w') as f:
        cnx = irutils.DBConnection()
        f.write('DeviceType,Brand,CodesetCount\n')
        report(cnx, f)
        f.close()

if __name__ == '__main__':
    list_codesets_per_brand_type()