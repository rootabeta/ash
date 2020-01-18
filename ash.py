try:
    import time as t
    import paramiko
    import subprocess
    import sys
    import getpass
except:
    exit(0)
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
    print(ip)
    ip=str(ip)
except:
    print("Resolution error - may resolve over regular DNS! Abort in the next 5 seconds if this is important to you...")
    for i in range(0,5):
        sys.stdout.write("{}... ".format(5-i)) ; sys.stdout.flush()
        t.sleep(1)

    print("\nHave it your way")

    ip = str(host)

port = 22

ssh=paramiko.SSHClient()
ssh.load_system_host_keys()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

while True:
    try:
        debug("Attempting to connect.")
        ssh.connect(ip,int(port),username=str(user),password=str(password),timeout=None,look_for_keys=False,pkey=None,key_filename=None)
        break
    except KeyboardInterrupt:
        debug("User requested interrupt.")
        sys.exit(0)
    except paramiko.ssh_exception.AuthenticationException:
        debug("Authentication Error.")
        sys.exit(0)
    except Exception as e:
        debug("Generic error.")
        debug(e)
        sys.exit(1)
prompt="ash>"
ssh.invoke_shell()
debug("Connection established!")
print("Note: this is a rudimentary shell at best - you will not be able to change dir or anything fancy. press Ctrl-C to exit.")
while True:
    try:
        cmd=input(prompt)
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd)
        line = None
        while True:
            line=ssh_stdout.readline()
            sys.stdout.write(line)
            if not line: 
                sys.stdout.flush()
                break

    except KeyboardInterrupt:
        print("User requested interrupt. Shutting down cleanly...")
        ssh.close()
        sys.exit(0)
    except Exception as f:
        print(f)
