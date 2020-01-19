import socks #pip3 install PySocks
import telnetlib
import os
import time as t
import paramiko
import subprocess
import sys
import getpass
import argparse

if sys.version_info[0] != 3:
    exit("Requires python3")

def debug(string,debug=True,verbose=True):
    string = "[DEBUG] {}".format(string)
    if debug:
        if verbose:
            print(string)
        else:
            return(string)

parser = argparse.ArgumentParser(description='Anonymous SSH client over tor')
parser.add_argument('host',type=str,help='hostname to connect to',nargs=1)
parser.add_argument('-p',dest='port',type=int,help='port to connect to',nargs=1,required=False,default=22)
parser.add_argument('--tor-port',dest='torport',type=int,help='tor proxy port',nargs=1,required=False,default=[9050])
parser.add_argument('-u',dest='user',type=str,help='username',nargs=1,required=False)

arguments = parser.parse_args()
arguments = vars(arguments)
if arguments['user']:
    user = arguments['user'][0]
else:
    user = None
host = arguments['host'][0]
port = int(arguments['port'])
torport = arguments['torport'][0]

try:
    user,host = host.split("@",1)
except:
    if not user:
        user = input("username: ")

debug("USER: {} | HOST: {} | PORT: {} | TOR PORT: {}".format(user,host,port,torport))

password = getpass.getpass("{}@{}'s password: ".format(user,host))

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
                port=torport
        )
        debug("Connecting...")
        try:
            proxy.connect((str(ip),int(port)))    
        except:
            exit("Error: proxy connection failed.")
        
        ssh=paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        ssh.connect(ip,int(port),banner_timeout=3,username=str(user),password=str(password),timeout=None,look_for_keys=False,allow_agent=False,pkey=None,key_filename=None,sock=proxy)
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

debug("Spawning interactive channel")

term = subprocess.check_output('echo $TERM',shell=True).split()
rows, columns = os.popen('stty size', 'r').read().split()
term = term[0]
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
