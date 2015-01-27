import pexpect
serverlist = ["54.251.110.12", "54.251.110.3", "54.251.109.253", "54.251.109.250",
              "54.251.240.47", "46.137.246.229", "175.41.143.31", "54.251.212.185"]

for eachserver in serverlist:
    try:
        print eachserver
        telnetcmd = "telnet %s 11211" % (eachserver)
        print telnetcmd
        child = pexpect.spawn(telnetcmd)
        matchstring = "Connected to *"
        child.expect(matchstring)
        child.sendline('flush_all')
        child.expect('OK')
        child.sendline('quit')
    except Exception, e:
        print e
        pass