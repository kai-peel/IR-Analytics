import json as simplejson
import urllib2
#import serial
import os
import threading
import glob
import time
import socket
import MySQLdb
import scipy.stats
import pexpect
from time import strftime
from datetime import datetime
DBTOCONNECT="54.251.240.47"  # "175.41.143.31"

class DBConnection:
    
    def __init__(self, DBServer,DBUser,DBPass): 
        self.dbconn=None
        self.dbcursor=None 
        try:
            self.dbconn=MySQLdb.connect(host=DBServer,user=DBUser, passwd=DBPass,db="devices",connect_timeout=5)
            self.dbcursor=self.dbconn.cursor() 
        except Exception ,e:
            print e
            

def getIRStream(uesid):
        headers = { 'User-Agent' : "Peel" }
        req="http://samsungir.peel.com/targets/uesid/%d" %uesid
        request = urllib2.Request(req,headers=headers)
        response=urllib2.urlopen(request)
        uesdata = simplejson.loads(response.read())
        #print uesdata
        return uesdata

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
       dbconnection = DBConnection(DBTOCONNECT,"zdbadmin","z3l4yi23")
       #dbconnection.dbcursor.execute("select distinct uesid from uescodes a, codesets b where a.codesetid = b.codesetid and b.activeflag='Y' and a.activeflag='Y'  and ifnull(codetype,'Full_Repeat') <> 'Toggle' and a.codesetid = 400020 and encodedbinary is null") 
      # dbconnection.dbcursor.execute("select distinct uesid from uescodes where uesid > 182000 and encodedbinary is null") 
       dbconnection.dbcursor.execute("""select a.uesid from uescodes a, codesets b, uesidfunctionmap c
where a.uesid = c.uesid and c.codesetid = b.codesetid 
and b.activeflag = 'Y' and encodedbinary is null and exists ( select 1 from uespulses d where d.uesid = c.uesid) and c.activeflag ='Y' order by a.uesid desc """)
       timestampsuffix=strftime("%Y%m%d%H%M%S")
       logfilename="c:/log/fprt_%s.txt" %(timestampsuffix)
       errfilename="c:/log/fprt_err_%s.txt" %(timestampsuffix)
       logfile=open(logfilename,'w')
       errfile=open(errfilename,'w')

       start_time = datetime.now()
       logfile.write("Started: %s\n" % start_time)

       failedues=[]
       uesidlist = dbconnection.dbcursor.fetchall()
       #uesidlist = [180905,180906,180907,180908,180909,180910,180911,180912,180913,180914,180915,180916,180917,180918,180919,180920,180921,180922,180923,180924,180925,180926,180927,180928,180929,180930,180931,180932,180933,180934,180935,180936,180937,180938,180939,180940]
       #uesidlist =
       print uesidlist
       #logfile.write('%s\n' % uesidlist)
       for eachuesid in  uesidlist:
           print eachuesid[0]
           logfile.write('%d\n' % eachuesid[0])
           try:
               #irstream=getIRStream(eachuesid[0])
               #if len(irstream["mainframe"].split(" ")) > 2 :
               #    fullpulse=converttonumbers(irstream["mainframe"].split(" "))
               #else:
               #    fullpulse=converttonumbers(irstream["toggleframe1"].split(" "))
               dbconnection.dbcursor.execute("SELECT pulse FROM uespulses where uesid=%d order by seq " % eachuesid[0])
               p = dbconnection.dbcursor.fetchall()
               fullpulse = []
               for each_pulse in p:
                   fullpulse.append(each_pulse[0])

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
                   print updatequery
                   logfile.write('%s\n' % updatequery)
                   dbconnection.dbcursor.execute(updatequery)
                   dbconnection.dbconn.commit()
           except Exception,e:
               print e
               errfile.write('%s\n' % e)
       dbconnection.dbcursor.close()
       #clearcache()

       end_time = datetime.now()
       logfile.write("Ended: %s\n" % end_time)
       logfile.write("Duration: %s\n" % (end_time - start_time))

       logfile.close()
       errfile.close()


def clearcache():
    serverlist = [
    "ec2-54-251-85-147.ap-southeast-1.compute.amazonaws.com","ec2-54-251-200-113.ap-southeast-1.compute.amazonaws.com","ec2-122-248-225-147.ap-southeast-1.compute.amazonaws.com","ec2-54-254-21-136.ap-southeast-1.compute.amazonaws.com"]
    
    for eachserver in serverlist:
        print eachserver
        telnetcmd= "telnet %s 11211" %(eachserver)
        print telnetcmd
        child = pexpect.spawn (telnetcmd)
        matchstring="Connected to *"  
        child.expect (matchstring)
        child.sendline ('flush_all')
        child.expect ('OK')
        child.sendline ('quit')
        print "Cache Cleared"
           

       
if __name__ == '__main__':
    main()
