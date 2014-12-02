import scipy.stats
import irutils
#DBTOCONNECT="175.41.143.31"  # production
DBTOCONNECT = "54.254.101.29"  # staging
DBTABLE = "user_ir_capture_"
DBTBCNT = 20

def converttonumbers(charlist):
    numlist=[]
    for eachchar in charlist:
        numlist.append(int(eachchar))
    return numlist


def findsmalllow(pulselist):
    smalllow=[]
    for i in range(2,len(pulselist),2):
        if pulselist[i]> 700:
            break;
        smalllow.append(pulselist[i])
    return int(scipy.stats.mode(smalllow, axis=0)[0][0])


def findhigh(pulselist):
    smallhigh=[]
    for i in range(3,len(pulselist)-1,2):
        if pulselist[i]> 700:
            break;
        smallhigh.append(pulselist[i])
    return int(scipy.stats.mode(smallhigh, axis=0)[0][0])


def findalthigh(pulselist,smallhigh):
    althigh=[]
    for i in range(3,len(pulselist)-1,2):
        if pulselist[i]> 700:
            break;
        if abs(pulselist[i]-smallhigh) > 4:
            althigh.append(pulselist[i])
    if len(althigh)==0:
        return None
    else:
        return int(scipy.stats.mode(althigh, axis=0)[0][0])


def findaltlow(pulselist,smalllow):
    althigh=[]
    for i in range(2,len(pulselist),2):
        if pulselist[i]> 700:
            break;
        if abs(pulselist[i]-smalllow) > 4:
            althigh.append(pulselist[i])
    if len(althigh)==0:
        return None
    else:
        return int(scipy.stats.mode(althigh, axis=0)[0][0])


def findbinvalue(pulselist,on1,on2,off1,off2):
    binvalue=[]
    try:
        for i in range(2,len(pulselist)-2,2):
            if pulselist[i]> 700 or pulselist[i+1]> 700 :
                break;
            if ((abs(pulselist[i]-on1) < 4) and (abs(pulselist[i+1]-off1) < 4)):
                binvalue.append('0')
            elif ((abs(pulselist[i]-on2) < 4) and (abs(pulselist[i+1]-off1) < 4)):
                binvalue.append('1')
            elif ((abs(pulselist[i]-on1) < 4) and (abs(pulselist[i+1]-off2) < 4)):
                binvalue.append('1')
            elif ((abs(pulselist[i]-on2) < 4) and (abs(pulselist[i+1]-off2) < 4)):
                binvalue.append('1')
            else:
                binvalue.append('0')
                #print "Weird value %d:%d at position %d, Zero is %d:%d , One is %d:%d "  %(pulselist[i],pulselist[i+1],i,on1,off1,on1,off2)
                #return '0x00000000'
        return hex(int('0b'+''.join(binvalue),2))
    except Exception,e:
        return '0x00000000'


def main():
    log = irutils.Logger("htc")
    cnx = irutils.DBConnection(DBTOCONNECT, "kai")
    for idx in xrange(DBTBCNT):
        query = "SELECT id, frame FROM %s%02d WHERE frame != 'None' and encodedbinary IS NOT NULL" % (DBTABLE, idx)
        try:
            cnx.cursor.execute(query)
            captures = cnx.cursor.fetchall()
            for id, frame in captures:
                if frame and len(frame) and frame != "None":
                    print "convert [%d] %s..." % (id, frame)
                    try:
                        fullpulse = converttonumbers(frame.split(','))
                        if len(fullpulse) > 7:
                            on1 = findsmalllow(fullpulse)
                            off1 = findhigh(fullpulse)
                            off2 = findalthigh(fullpulse, off1)
                            if off2 is None:
                                on2 = findaltlow(fullpulse, on1)
                            else:
                                on2 = 0
                            binvalue = findbinvalue(fullpulse, on1, on2, off1, off2)
                            updatequery = "UPDATE %s%02d SET encodedbinary = '%s' WHERE id = %d;" % (DBTABLE, idx, str(binvalue)[2:], id)
                            cnx.cursor.execute(updatequery)
                            cnx.db.commit()
                    except Exception, e:
                        print "ERR:%d: %s." % (id, e)
            cnx.cursor.close()
            #clearcache()
        except Exception, e:
            print e


if __name__ == '__main__':
    main()
