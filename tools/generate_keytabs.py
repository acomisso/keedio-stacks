#!/usr/bin/env python
# This script takes teh CVS file generated by ambari with information about principals and keytabs, 
# creates script that generates, deploy them and purge them

import time,os
import sys,getopt 
import socket 
import string 
# getting command line arguments
def help():
         print "Usage:" 
	 print sys.argv[0], "-s server filename.cvs"

args=sys.argv[1:]
try: 
	options, arguments = getopt.getopt(sys.argv[1:], 's:h', ['server','help'])
except getopt.GetoptError:
	help()
        sys.exit(2)

if len(arguments) != 1:
	print "Wrong number of arguments!\n"
        help()
        sys.exit(3)
filename=arguments[0]

# getting full path fo the file
cwd=os.getcwd() 
input=os.path.join(cwd,filename)

print "Opening file", input


#Defaulting the IPA server to the FQDN of the localhost
ipaserver=socket.getfqdn()
for opt, arg in options:
	if opt in ('-s','--server'):
		ipaserver=arg
	elif opt in ('-h','--help'):
		help()
                sys.exit(2) 


print "Using Kerberos server:",ipaserver


ts=time.time()

#creates a temporary dir
output_dir="/tmp/ambari_kerberos"
os.popen("mkdir -p "+output_dir)

generate=open(output_dir+"/generate.sh",'w')
deploy=open(output_dir+"/deploy.sh",'w')
purge=open(output_dir+"/purge.sh",'w')

keytabs_dir=output_dir+"/"+str(ts)

keytabsToGen=dict()
try:
  with open(input) as f:
    for line in f:
        host,desc,principal,file,directory,owner,group,mode=line.split(',')
        file=directory+'/'+file 
        principal=principal.split('@')[0]
        if not principal in keytabsToGen:
            keytabsToGen[principal]=dict()
        if not host in keytabsToGen[principal]:
            keytabsToGen[principal][host]=dict()
        if not file in keytabsToGen[principal][host]:
            keytabsToGen[principal][host][file]={'owner':owner,'group':group,'mode':mode}

        #Since Httpfs is not installed as component, but it is integrated in hadoop, we needs to generate here its principal and keytabs
        # We genearte the httpfs services on the same nodes were namemodes are running
        if str(principal[0:2]) == "nn":
            principal_httpfs="httpfs"+principal[2:]
            print "Adding principal", principal_httpfs
            if not principal_httpfs in keytabsToGen:
                 keytabsToGen[principal_httpfs]=dict()
            if not host in keytabsToGen[principal_httpfs]:
                 keytabsToGen[principal_httpfs][host]=dict()
            if not file in keytabsToGen[principal_httpfs][host]:
                 keytabsToGen[principal_httpfs][host]['/etc/security/keytabs/httpfs.service.keytab']={'owner':'httpfs','group':'hadoop','mode':'400'}
  f.close()
except: 
  print "ERROR: reading the file",input
  sys.exit(4) 

help_keytab="/tmp/ambari_kerberos/" + str(ts) + "/help.keytab"
generate.write("echo 'Getting kerberos Admin credentials'\n")
generate.write("kinit admin || { echo 'Kerberos authentication failed' ; exit 1; }\n")
generate.write("mkdir -p %s\n" % keytabs_dir)

purge.write("echo 'Getting kerberos Admin credentials'\n")
purge.write("kinit admin || { echo 'Kerberos authentication failed' ; exit 1; }\n")
purge.write ("rm -rf %s\n" % keytabs_dir)
for principal in keytabsToGen:
    print principal
    generate.write("#========================================================\n")
    generate.write("#=====================%s=====================\n" % principal)
    generate.write("#========================================================\n")
    generate.write("rm -f " + help_keytab + "\n")
    if '/' in principal:
    # It's a service
        generate.write("ipa service-add --force %s\n" % principal)
        purge.write("ipa service-del %s\n" % principal)
           
		 
    else:
        generate.write("ipa user-add " + principal + " --first SYSTEM --last SYSTEM\n")
        purge.write("ipa user-del %s\n" % principal)
    generate.write("ipa-getkeytab -s %s -p %s -k %s\n" % (ipaserver,principal,help_keytab))
    for host in keytabsToGen[principal]:    
        for file in keytabsToGen[principal][host]:
            generate.write("mkdir -p %s/%s%s\n" % (keytabs_dir,host,os.path.dirname(file)))
            generate.write("ktutil << EOF\n" + 
              "read_kt " + keytabs_dir + "/" + host + file + "\n" + 
              "read_kt " + help_keytab + "\n" +
              "write_kt " + keytabs_dir + "/" + host + file + "\n" +
              "EOF\n")

            file_details=keytabsToGen[principal][host][file]
            owner=file_details['owner']
            group=file_details['group']
            mode=file_details['mode'].replace('\n','')
            deploy.write("ssh " + host + " 'mkdir  -p " + os.path.dirname(file) + "'\n")
            deploy.write("echo 'Installing keytab "+file+" on host "+host+"'\n")
            deploy.write("scp " + keytabs_dir + "/" + host + "/" + file + " " + host + ":" + file + "\n")
            purge.write("echo 'removing keytab "+file+" from host "+host+"'\n") 
            purge.write("ssh " + host + " 'rm -rf "+file+"'\n")
            deploy.write("ssh " + host + " 'chown " + owner + ":" + group + " " + file + "'\n")
            deploy.write("ssh " + host + " 'chmod " + mode + " " + file + "'\n\n")
generate.close()
deploy.close()
purge.close()
