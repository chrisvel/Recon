#!/usr/bin/python
import socket
import sys
import multiprocessing
import recon
import subprocess

if len(sys.argv) != 2:
    print "Usage: smtprecon.py <ip address>"
    sys.exit(0)

ip_address = sys.argv[1]

recon.checkpath("./results/{0}".format(ip_address))

print('\033[1;34m[*]  Performing nmap SMTP script scan for {0}\033[1;m'.format(ip_address))
if not recon.checknmaprun(ip_address, "_nmap_scan_smtp.xml"):
    SMTPSCAN = "nmap -vv -sV -Pn -p 25,465,587 --script-args=unsafe=1 --script=smtp-vuln* -oN './results/{0}/{0}_smtp.nmap' -oX './results/{0}/{0}_nmap_scan_smtp.xml' {0}".format(ip_address)
    results = subprocess.check_output(SMTPSCAN, shell=True)
else:
    print('\033[1;34m[*]  Allready performed nmap SMTP script scan for {0} Skipping..\033[1;m'.format(ip_address))

# Test for presence of the VRFY command
print('\033[1;34m[*]  Trying SMTP Enum on {0}\033[1;m'.format(ip_address))
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connect = s.connect((ip_address,25))
banner = s.recv(1024)
s.send('HELO test@test.org \r\n')
result = s.recv(1024)
s.send('VRFY ' + "TEST" + '\r\n')
result = s.recv(1024)
if ("not implemented" in result) or ("disallowed" in result):
    s.close()
    print('\033[1;34m[*]  VRFY command not implemented on {0}\033[1;m'.format(ip_address))
else:
    print('\033[1;32m[*]  VRFY command is enabled on {0} starting bruteforce\033[1;m'.format(ip_address))

    names = open('/usr/share/dnsrecon/namelist.txt', 'r')
    for name in names:
        name = str(name.strip())
        s.send('VRFY {0} \r\n'.format(name))
        result = s.recv(1024)
        if (("250" in result) or ("252" in result) and ("Cannot VRFY" not in result)):
            print('\033[1;32m[*]  SMTP VRFY Account found on {0} : {1}\033[1;m'.format(ip_address, name))
            outfile = "results/{0}/{0}_smtprecon.txt".format(ip_address)
            f = open(outfile, "w")
            f.write("[*]  SMTP VRFY Account found on {0} : {1}".format(ip_address, name))
            f.close

    s.close()
    sys.exit()

