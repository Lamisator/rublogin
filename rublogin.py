#!/usr/bin/python3

import requests, getpass, socket, platform, subprocess, time, os, sys, getopt

verb = 0
loginid = ""
pw = ""

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
	dbgmsg("Trying to determine: OS...")
	if platform.system() == "Windows":
		dbgmsg("Windows detected.")
		res = subprocess.call(["ping", host, "-n 1"])
	else:
		dbgmsg("UNIX(-like) OS detected.")
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
def logout():
	dbgmsg("Trying to log out...")
	ip = get_ip_address()
	if ip == 0:
		print("Network is unreachable.\n")
		return 0
	payload = {'code': '1', 'loginid': '', 'password': '', 'ipaddr': ip, 'action': 'Logout'}
	text = ""
	try:
		dbgmsg("Trying to log out via HTTP-POST...")
		r = requests.post("https://login.rz.ruhr-uni-bochum.de/cgi-bin/laklogin", data=payload)
		text = r.text
	except Exception:
		print("An error occured while trying to logout.\n")
	if "erfolgreich" in text:
		print("O.K., successfully logged out.")
		return 1
	else:
		print("Fail.")
		return 0

def login(watchdog, interval):
	global loginid, pw
	loginid = input("Login ID: ")
	pw = getpass.getpass()
	if establish_connection(loginid, pw) == 0:
		exit()
	if watchdog:
		wd_enabled = 1
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

def dbgmsg(msg):
	if verb: print("Dbg: " + msg) 
	return

def print_help():
	print("Usage:\n -l / --logout : Terminates the current HIRN-Port-Session\n -w / --watchdog [interval]: Enables the watchdog. Checks the status of the connection every [interval] seconds and reconnects, if neccessary\n -v / --verbose : Prints debug messages throughout the login/logout process\n -h / --help : Displays this help")
def main(argv):
	global verb
	logout_v = 0
	watchdog = 0
	interval = 0
	try:
		opts = getopt.getopt(argv, "hvlw:", ["help","verbose","logout","watchdog="])	
	except Exception:
		verb = 0
		print("Invalid arguments. Use the -h parameter if you are lost.")
		sys.exit()
	for opt, arg in opts:
		if opt in ("-h", "--help"):
			print_help()
			sys.exit()
		elif opt in("-v",  "--verbose"):
			verb = 1
			print("Debugging messages enabled.")
		elif opt in ("-l", "--logout"):
			logout_v = 1
		elif opt in ("-w", "--watchdog"):
			watchdog = 1
			try:
				interval = int(arg)
			except ValueError:
				print("Only integers, please. Aborting.")
				sys.exit()
			if interval < 5:
				print("Interval must be 5 seconds or longer. Aborting.")
				sys.exit()
			print("Watchdog enabled.")
	if logout_v:
		logout()
	else:
		login(watchdog, interval)
main(sys.argv[1:])

