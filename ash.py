try:
    import socks #pip3 install PySocks
    import telnetlib
    import os
    import time as t
    import paramiko
    import subprocess
    import sys
    import getpass
except:
    exit("Dependancy error")

if sys.version_info[0] != 3:
    exit("Requires python3")

print(" _____ _____ _____ ")
print("|  _  |   __|  |  |")
print("|     |__   |     |")
print("|__|__|_____|__|__|")
print("       [ASH]       ")
print("  An SSH over tor  ")
print("-------------------")
print("\nWARNING: This program requires tor to be running in the background on port 9050.")

try:
    host = sys.argv[1]
except:
    exit("Error - expected argument")

try:
    port = sys.argv[2]
except:
    port = 22

try:
    user,host = host.split("@",1)
except:
    user = input("username: ")

password = getpass.getpass("password: ")

def debug(string,debug=True,verbose=True):
    string = "[DEBUG] {}".format(string)
    if debug:
        if verbose:
            print(string)
        else:
            return(string)

try:
    p = subprocess.Popen("tor-resolve {}".format(str(host)), stdout=subprocess.PIPE, shell=True)
    ip=p.communicate()
    ip = ip[0].decode('utf-8').strip("\n")
    debug("Resolved to {}".format(ip))
    ip=str(ip)
except:
    print("Resolution error - may resolve over regular DNS! Abort in the next 5 seconds if this is important to you...")
    for i in range(0,5):
        sys.stdout.write("{}... ".format(5-i)) ; sys.stdout.flush()
        t.sleep(1)

    print("\nHave it your way")

    ip = str(host)

port = 22

#ssh=paramiko.SSHClient()
##ssh.load_system_host_keys()
#ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

while True:
    try:
        debug("Attempting to connect.")
        #proxy = paramiko.ProxyCommand('tor --SocksPort 4172')
        proxy = socks.socksocket()
        proxy.set_proxy(
                proxy_type=socks.SOCKS4,
                addr='localhost',
                port=9050
        )
        debug("Connecting...")
        proxy.connect((str(ip),int(port)))    
        #debug("Connected to proxy")
        #transport = paramiko.Transport(proxy)
        #transport.connect() 
        #debug("Transport online")
        #ssh = paramiko.client.SSHClient.connect(ip,int(port),username=str(user),password=str(password),timeout=None,look_for_keys=False,allow_agent=False,pkey=None,key_filename=None,sock=proxy)
        
        #####-----#####

        ssh=paramiko.SSHClient()
        #ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        ssh.connect(ip,int(port),username=str(user),password=str(password),timeout=None,look_for_keys=False,allow_agent=False,pkey=None,key_filename=None,sock=proxy)
        print(ssh._transport.get_banner())
        break
    except KeyboardInterrupt:
        print("User requested interrupt.")
        sys.exit(0)
    except paramiko.ssh_exception.AuthenticationException:
        print("Authentication Error.")
        sys.exit(0)
    except Exception as e:
        print("Generic error.")
        debug(e)
        sys.exit(-1)
prompt="ash>"
#ssh.get_pty()

term = subprocess.check_output('echo $TERM',shell=True).split()
rows, columns = os.popen('stty size', 'r').read().split()
term = term[0]
debug(term)
chan = ssh.invoke_shell(term=term,width=int(rows),height=int(columns))


telnet = telnetlib.Telnet()
telnet.sock = chan #The syntax to play with this looks a lot like a regular socket.... ;)
try:
    telnet.mt_interact()
except:
    print("Proxy socket closed")
chan.close()
telnet.close()
proxy.close()
