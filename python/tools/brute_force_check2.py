import MySQLdb
import time
import ir_util4
IR_CODE_DATABASE = "175.41.143.31"  # production


class DBConnection:
    def __init__(self, host, user, passwd):
        self.db = MySQLdb.connect(host=host, user=user, passwd=passwd, db="devices")
        self.cursor = self.db.cursor()

    def __del__(self):
        self.cursor.close()
        self.db.close()


class Logger:
    def __init__(self, tag):
        time_stamp_suffix = time.strftime("%Y%m%d%H%M%S")
        log_filename = "%s_%s.txt" % (tag, time_stamp_suffix)
        self.log = open(log_filename, 'w')

    def __del__(self):
        self.log.close()


def print_duplicate_function_names(log, cnx, codeset, value):
    query = ("SELECT DISTINCT f.functionname FROM uescodes c "
             "JOIN uesidfunctionmap m ON m.uesid = c.uesid "
             "JOIN functions f ON f.id = m.functionid "
             "WHERE m.codesetid = %d AND c.encodedbinary ='%s' " %
             (codeset, value))
    try:
        cnx.cursor.execute(query)
        r = cnx.cursor.fetchall()
        if cnx.cursor.rowcount > 1:
            for i in xrange(cnx.cursor.rowcount):
                log.log.write("%s," % r[i][0])
    except Exception, e:
        print e


def get_power_off(log, cnx, codeset):
    query = ("SELECT encodedbinary FROM uescodes c "
             "JOIN uesidfunctionmap m ON m.uesid = c.uesid "
             "WHERE m.codesetid = %d AND m.functionid = 48 " %
             codeset)
    try:
        cnx.cursor.execute(query)
        r = cnx.cursor.fetchall()
        if cnx.cursor.rowcount > 0:
            log.log.write("|%s|" % r[0][0])
            return r[0][0]
        return 'None'
    except Exception, e:
        print e


def main():
    log = Logger("fcombo")
    cnx = DBConnection(IR_CODE_DATABASE, "zdbadmin", "z3l4yi23")

    log.log.write("%s|%s|%s|%s|%s|%s|%s\n" % ("Brand", "Codeset ID",  "PowerOn", "Same as PowerOn", "Power_Off", "Same as Power_Off", "PowerOn=Power_Off"))

    query = ("SELECT f.uesid, b.brandname, f.codesetid, c.encodedbinary FROM uesidfunctionmap f "
             "JOIN codesets s ON f.codesetid = s.codesetid "
             "JOIN brands b ON b.brandid = s.brandid "
             "JOIN uescodes c ON c.uesid = f.uesid "
             "WHERE f.activeflag ='Y' AND s.activeflag = 'Y' "
             "AND f.functionid = 48 AND c.codetype = 'FCOMBO' ")
    try:
        cnx.cursor.execute(query)
        r = cnx.cursor.fetchall()
        if cnx.cursor.rowcount > 0:
            for i in xrange(cnx.cursor.rowcount):
                log.log.write("%s|%d|%s|" % (r[i][1], r[i][2], r[i][3]))
                codeset = r[i][2]
                poweron_value = r[i][3]
                if poweron_value and len(poweron_value) > 0 and poweron_value != 'None':
                    print_duplicate_function_names(log, cnx, codeset, poweron_value)
                    poweroff_value = get_power_off(log, cnx, codeset)
                    if poweroff_value and len(poweroff_value) > 0 and poweroff_value != 'None':
                        print_duplicate_function_names(log, cnx, codeset, poweroff_value)
                        if poweron_value == poweroff_value:
                            log.log.write("|X")
                log.log.write('\n')
                log.log.flush()
    except Exception, e:
        print e


if __name__ == '__main__':
    main()
