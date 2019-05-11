try:
    import time as t
    import paramiko
    from subprocess import *
    import sys
    from pwn import *
except:
    print("Missing vital packages. Installing...")
    import os
    os.system("pip install paramiko")
    os.system("pip install pwntools")
    sys.exit(0)
print(" _____ _____ _____ ")
print("|  _  |   __|  |  |")
print("|     |__   |     |")
print("|__|__|_____|__|__|")
print("       [ASH]       ")
print("  An SSH over tor  ")
print("-------------------")
print("\nWARNING: This program requires tor to be running in the background on port 9050.")
host=raw_input("Host: ")
p = subprocess.Popen("tor-resolve "+str(host), stdout=subprocess.PIPE, shell=True)
ip=p.communicate()
ip=str(ip)
ip=ip.replace("('","")
ip=ip.replace("\n","")
ip=ip.replace("'","")
ip=ip.replace(", None","")
ip=ip.replace("\n)","")
ip=ip[:-3]
ip=str(ip)
port=raw_input("Port: ")
if port=="":
    port=22
user=raw_input("Username: ")
pswd=raw_input("Password: ")
ssh=paramiko.SSHClient()
ssh.load_system_host_keys()
paramiko.set_missing_host_key_policy(paramiko.AutoAddPolicy())
log.info("Host: "+str(ip))
log.info("Port: "+str(port))
log.info("Username: "+user)
log.info("Password: "+pswd)
while True:
    try:
        log.info("Attempting to connect.")
        ssh.connect(ip,int(port),username=str(user),password=str(pswd),timeout=None,look_for_keys=False,pkey=None,key_filename=None)
        break
    except KeyboardInterrupt:
        log.failure("User requested interrupt.")
        sys.exit(0)
    except paramiko.ssh_exception.AuthenticationException:
        log.failure("Authentication Error.")
        sys.exit(0)
    except:
        log.failure("Generic error.")
        sys.exit(1)
prompt="ash>"
ssh.invoke_shell()
log.success("Connection established!")
while True:
    try:
        cmd=raw_input(prompt)
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd)
        line=mystdout.readline()
        if not line: 
            pass
        print str(line)
    except KeyboardInterrupt:
        log.failure("User requested interrupt. Shutting down cleanly...")
        ssh.close()
        sys.exit(0)
    except:
        log.failure("Generic error. Something's wrong, but we'll power through it...")
