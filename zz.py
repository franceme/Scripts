#!/usr/bin/env python3
'''####################################
#Version: 00.00
#Version Numbering: Major.Minor
#Reasons for imports
		os							  : used for verifying and reading files
		sys					 : used for exiting the system
'''####################################

##Imports
import os
import sys
import subprocess
import platform
import socket

'''####################################
#The main runner of this file, intended to be ran from
'''####################################

computers = {
	"=":{},
	"self":{
			"user":os.path.expanduser('~').split('/')[-1],
			"ip":"127.0.0.1",
			"port":22,
			"sudo":False,
	}
}

def dir_of(path):
	return os.path.abspath(path)

cur_dir = lambda:dir_of(os.curdir)

def open_port():
	"""
	https://gist.github.com/jdavis/4040223
	"""
	sock = socket.socket()
	sock.bind(('', 0))
	x, port = sock.getsockname()
	sock.close()

	return port

def checkPort(port):
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	result = bool(sock.connect_ex(('127.0.0.1', int(port))))
	sock.close()
	return result

def try_port(port):
	if checkPort(port):
		return port
	else:
		return open_port()

remote_file = lambda remote,file:  file.strip().replace('__/','/home/' + remote['user'] + '/Downloads/').replace('_/', '/home/' + remote['user'] + '/').strip()

def getArgs():
	import argparse
	parser = argparse.ArgumentParser("ZZ new aide")
	parser.add_argument("-n","--name", help="The name of the endpoint", nargs=1, default="remote")
	parser.add_argument("-f","--foil", help="The location file of additional computers", nargs='?', default=None)
	parser.add_argument("-p","--ports", help="The ports to be exposed", nargs="*", default=[])
	parser.add_argument("-c","--cmd", help="The cmd to be run", nargs="*", default=[])
	parser.add_argument("--ssh", help="Change the ssh port", nargs="?", default=None)
	parser.add_argument("--upload",help="Upload the file", nargs="?", default=None)
	parser.add_argument("--download",help="Download the file", nargs="?", default=None)
	parser.add_argument("--sdel", help="Delete the file (only for the upload/download)",action='store_true',default=False)
	parser.add_argument("--jupyter", help="Run JupyterLab",action='store_true',default=False)
	parser.add_argument("--splunk", help="Run Splunk",action='store_true',default=False)
	parser.add_argument("--vagrant", help="Run Vagrant",action='store_true',default=False)
	parser.add_argument("--pyqodana", help="Run PyQodana",nargs="?", default=None)
	parser.add_argument("--jqodana", help="Run Java Qodana",nargs="?", default=None)
	parser.add_argument("--results", help="Any Results Directory",nargs="?", default="RunResults")
	return parser.parse_args()

def run(remote,cmd='',port=''):
	run_cmd = 'sudo su' if remote['sudo'] else ''
	if cmd.strip() != '':
		run_cmd = cmd
	#return f"ssh -t {remote['port']} {port} {remote['user']}@{remote['ip']} {run_cmd}"
	if remote['ip'] != '127.0.0.1':
		return f"ssh -t {port} {remote['user']}@{remote['ip']} {run_cmd}"
	else:
		return run_cmd


def down(remote,file):
	#return f"scp -t {remote['port']} {remote['user']}@{remote['ip']}:{file} ./"
	return f"scp {remote['user']}@{remote['ip']}:{remote_file(remote,file)} ./"

def up(remote,file):
	#return f"scp -t {remote['port']} {file.strip()} {remote['user']}@{remote['ip']}:/tmp/"
	return f"scp {file.strip()} {remote['user']}@{remote['ip']}:/tmp/"

if __name__ == '__main__':
	args = getArgs()

	if args.foil and os.path.exists(args.foil):
		import json
		with open(args.foil,'r') as reader:
			computers = {**computers, **json.load(reader)}

	working_computers,cmds = [],[]

	if args.name[0] == "=":
		working_computers = [value for key,value in computers.items() if key != "=" and key != "self"]
	else:
		working_computers = [computers[args.name[0]]]

	for computer in working_computers:
		if args.ssh is not None:
			computer['port'] = args.ssh

		if args.jupyter:
			args.cmd = "sudo jupyter lab --allow-root".split()
			args.ports += ["8888"]
		elif args.splunk:
			args.cmd = f"sudo docker run -p 8000:8000 -v /home/{computer['user']}:/sync -e SPLUNK_START_ARGS='--accept-license' -e SPLUNK_PASSWORD='password' splunk/splunk:latest".split()
			args.ports += ["8000"]
		elif args.vagrant:
			print("Vagrant is not currently Setup and Ran")
			sys.exit(0)
			args.cmd = "apt-get install virtual-box vagrant".split()
			args.ports += ["8000"]
		elif args.pyqodana:
			#https://www.jetbrains.com/help/qodana/qodana-python-docker-readme.html#b920fd1
			args.pyqodana = os.path.abspath(args.pyqodana)
			path = '/'.join(args.pyqodana.split('/')[:-1])

			args.results = os.path.join(path, args.results)
			try:
				watch_cmd(f"yes|rm -r {args.results}/")
			except:
				pass
			args.cmd = f"docker run --rm -it -v {args.pyqodana}/:/data/project/ -v {args.results}/:/data/results/ jetbrains/qodana-python && mv {args.results} {args.pyqodana}".split()
		elif args.jqodana:
			#https://www.jetbrains.com/help/qodana/qodana-jvm-community-docker-readme.html#quick-start-recommended-profile
			args.jqodana = os.path.abspath(args.jqodana)
			path = '/'.join(args.pyqodana.split('/')[:-1])

			args.results = os.path.join(path, args.results)
			try:
				watch_cmd(f"yes|rm -r {args.results}/")
			except:
				pass
			args.cmd = f"docker run --rm -it -v {args.jqodana}/:/data/project/ -v {args.results}/:/data/results/ jetbrains/qodana-jvm-community && mv {args.results} {args.jqodana}".split()

		if args.download:
			cmds += [down(computer, args.download)]
			if args.sdel:
				cmds += [
					run(computer,f" \" yes|rm {remote_file(computer,args.download)} \"").replace('-t','')
				]
		elif args.upload:
			cmds += [up(computer, args.upload)]
			if args.sdel:
				cmds += [
					f"yes|rm {args.upload}"
				]
		else:
			ports = ""
			for port in set(args.ports):
				ports += f" -L {try_port(port)}:{computer['ip']}:{port} "

			cmds += [run(computer,' '.join(args.cmd), ports)]

	for x in cmds:
		print(x);os.system(x)
