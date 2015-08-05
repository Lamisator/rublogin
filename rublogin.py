import requests
import getpass
import socket
import platform
import subprocess
import time
import os
import sys

interval = 15
verb = 0

def get_ip_address():
	dbgmsg("Trying to obtain our current IP-Address...")
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.connect(("134.147.64.8", 80))
		dbgmsg("Success!")
		return s.getsockname()[0]
	except Exception:
		dbgmsg("Failure! Network unreachable.") 
		return 0
def ping(host):
	dbgmsg("Trying to determinate OS...")
	if platform.system() == "Windows":
		dbgmsg("Windows detected.")
		res = subprocess.call(["ping", host, "-n 1"])
	else:
		dbgmsg("Other, UNIX(-like) OS detected.")
		res = subprocess.call(["ping", "-c 1", host], stdin = subprocess.PIPE, stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL)
	dbgmsg("Pinging to see if our connection is up...")
	if res == 0:
		dbgmsg("We're connected!")
		return 1
	else:
		dbgmsg("Nope, no connection.")
		return 0
def establish_connection(user, pw):
	dbgmsg("Trying to establish connection...")
	ip = get_ip_address()
	if ip == 0:
		print("Network is unreachable.\n")
		return 0
	payload = {'code': '1', 'loginid': loginid, 'password': pw, 'ipaddr': ip, 'action': 'Login'}
	text = ""
	try:
		dbgmsg("Trying to log in via HTTP-POST...")
		r = requests.post("https://login.rz.ruhr-uni-bochum.de/cgi-bin/laklogin", data=payload)
		text = r.text
	except Exception:
		print("An error occured while trying to login.\n")
	if "Authentisierung gelungen" in text:
		print("O.K.")
		return 1
	else:
		print("Fail.")
		return 0
def dbgmsg(msg):
	if verb: print("Dbg: " + msg) 
	return

if(sys.argv[1] == "-v"):
	verb = 1
	print("Debugging messages enabled.")

loginid = input("Login ID: ") 
pw = getpass.getpass()
if establish_connection(loginid, pw) == 0:
	exit()
watchdog = input ("Enable connection watchdog? (y/n) ")
wd_enabled = 1
if watchdog == 'y':
	try:
		pid = os.fork()
	except OSError:
		sys.exit(1)
	if pid > 0:
		sys.exit(0)
	print("Watchdog-PID: " + str(os.getpid()) + "\n")

	while wd_enabled:
		time.sleep(interval)
		if(ping("8.8.8.8")):
			#print("O.K.")
			continue
		else:
			print("\nRUBLOGIN-Watchdog: Connection lost. Trying to re-establish...")
			establish_connection(loginid, pw)



