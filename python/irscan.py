__version__ = "1.0.0"
__date__ = "25-Nov-2014"

import scipy.stats
from time import strftime
from irutils import *


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
    log = Logger("fp")
    cnx = DBConnection("127.0.0.1")
    query = ("SELECT DISTINCT m.uesid FROM uescodes c, codesets s, uesidfunctionmap m "
             "WHERE m.uesid = c.uesid AND m.codesetid = s.codesetid "
             "AND s.activeflag = 'Y' AND m.activeflag = 'Y' "
             #"AND m.uesid IN (SELECT uesid from uespulses) "
             #"AND encodedbinary IS NULL "
             #"ORDER BY m.uesid "
            )





    #"select distinct uesid from uescodes a, codesets b where a.codesetid = b.codesetid
    # and b.activeflag='Y' and a.activeflag='Y'  and ifnull(codetype,'Full_Repeat') <> 'Toggle'
    # and a.codesetid = 400020 and encodedbinary is null")
    #"select distinct uesid from uescodes where uesid between 253440 and 288947 and length(encodedbinary) < 2")
    #"select a.uesid from uescodes a, codesets b, uesidfunctionmap c where a.uesid = c.uesid and c.codesetid = b.codesetid and b.activeflag = 'Y' and encodedbinary is null and exists ( select 1 from uespulses d where d.uesid = c.uesid) and c.activeflag ='Y' "

       #dbconnection.dbcursor.execute("select distinct uesid from uescodes a, codesets b where a.codesetid = b.codesetid and b.activeflag='Y' and a.activeflag='Y'  and ifnull(codetype,'Full_Repeat') <> 'Toggle' and a.codesetid = 400020 and encodedbinary is null")
      # dbconnection.dbcursor.execute("select distinct uesid from uescodes where uesid > 182000 and encodedbinary is null")





       failedues=[]
       uesidlist = dbconnection.dbcursor.fetchall()
       #uesidlist = [180905,180906,180907,180908,180909,180910,180911,180912,180913,180914,180915,180916,180917,180918,180919,180920,180921,180922,180923,180924,180925,180926,180927,180928,180929,180930,180931,180932,180933,180934,180935,180936,180937,180938,180939,180940]
       #uesidlist = 
       print uesidlist
       for eachuesid in  uesidlist:
           print eachuesid[0]
           try:
               irstream=getIRStream(eachuesid[0])
               if len(irstream["mainframe"].split(" ")) > 2 :
                   fullpulse=converttonumbers(irstream["mainframe"].split(" "))
               else:
                   fullpulse=converttonumbers(irstream["toggleframe1"].split(" "))
               if len(fullpulse) > 7:
                   on1=findsmalllow(fullpulse)
                   off1=findhigh(fullpulse)
                   off2=findalthigh(fullpulse,off1)
                   if off2 is None:
                       on2=findaltlow(fullpulse,on1)
                   else:
                       on2=0
                   binvalue=findbinvalue(fullpulse,on1,on2,off1,off2)
                   updatequery="update uescodes set encodedbinary='%s' where uesid = %d;" %(str(binvalue)[2:],int(eachuesid[0]))
                   print   updatequery
                   dbconnection.dbcursor.execute(updatequery)
                   dbconnection.dbconn.commit()
           except Exception,e:
               print e
       dbconnection.dbcursor.close()
       clearcache()
       logfile.close()
       errfile.close()

if __name__ == '__main__':
    main()
