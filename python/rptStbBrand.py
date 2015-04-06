#!/usr/bin/python
__author__ = 'kai'
import os
import codecs
from utils import irutils

LOGFILE = 'C:/Users/G50/Dropbox/Public/list_of_stb_brands_and_ids.csv'


def report(cnx, log):
    try:
        query = ("select a.brandid, a.brandname, c.country, c.displayname, count(*) "
                 "from brands a, codesets b, brandnames c "
                 "where a.brandid=b.brandid and a.brandid=c.brandid and devicetypeid=2 and activeflag='Y' "
                 "group by a.brandid, country order by brandname; ")
        cnx.cursor.execute(query)
        r = cnx.cursor.fetchall()
        for each in r:
            log.write('%s,%s,%s,%s,%d\n' % (each[0], each[1], each[2], each[3], each[4]))

    except Exception, e:
        print 'report: %s' % e


def main():
    try:
        os.remove(LOGFILE)
    except OSError:
        pass
    with codecs.open(LOGFILE, mode="w", encoding="utf-8") as f:
        cnx = irutils.DBConnection()
        f.write('BrandID,BrandName,CountryCode,Localization,CodesetCount\n')
        report(cnx, f)
        f.close()

if __name__ == '__main__':
    main()