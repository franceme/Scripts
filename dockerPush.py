#!/usr/bin/env python3


'''####################################
#Version: 00.00
#Version Numbering: Major.Minor
#Reasons for imports
os		: used for verifying and reading files
sys		: used for exiting the system
'''####################################

##Imports
import os
import sys
import subprocess
import platform
import socket

"""
sample forcing a docker container to run as su
docker run --rm -u 0 -it -v `pwd`:/temp username/dockername
 > -u 0
 > forcing the user id to be 0, the root id
"""

def is_docker():
	path = '/proc/self/cgroup'
	return (os.path.exists('/.dockerenv') or os.path.isfile(path) and
			any('docker' in line for line in open(path)))


docker = "docker"
docker_username = "frantzme"

'''####################################
#The main runner of this file, intended to be ran from
'''####################################


def run(cmd):
	return str(subprocess.check_output(cmd, shell=True, text=True)).strip()

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

def getPort(ports=[]):
	return ' '.join([
		f"-p {port if checkPort(port) else open_port()}:{port}" for port in ports
	])

dir = '%cd%' if sys.platform in ['win32','cygwin'] else '`pwd`'

def getDockerImage(input):
	if "/" not in input:
		use_lite = ":lite" in input
		if "pydev" in input:
			output = f"{docker_username}/pythondev:latest"
		elif "pytest" in input:
			output = f"{docker_username}/pytesting:latest"
		else:
			output = f"{docker_username}/{input}:latest"
		if use_lite:
			output = output.replace(':latest','') + ":lite"
		return output
	else:
		return input

def getArgs():
	import argparse
	parser = argparse.ArgumentParser("Dcokerpush = useful utilities for running docker images")
	parser.add_argument("-x","--command", help="The Docker image to be used", nargs=1, default="clean")
	parser.add_argument("-d","--docker", help="The Docker image to be used", nargs='*', default="frantzme/pydev:latest")
	parser.add_argument("-p","--ports", help="The ports to be exposed", nargs="*", default=[])
	parser.add_argument("-c","--cmd", help="The cmd to be run", nargs="?", default="/bin/bash")
	parser.add_argument("--dind", help="Use Docker In Docker", action="store_true", default=False)
	parser.add_argument("--detach", help="Run the docker imagr detached", action="store_true",default=False)
	parser.add_argument("--mount", help="mount the current directory to which virtual folder",default="/sync")
	parser.add_argument("-n","--name", help="The name of the image",default="kinde")
	return parser.parse_args()

def clean():
	global docker
	return [
			f"{docker} kill $({docker} ps -a -q)",
			f"{docker} kill $({docker} ps -q)",
			f"{docker} rm $({docker} ps -a -q)",
			f"{docker} rmi $({docker} images -q)",
			f"{docker} volume rm $({docker} volume ls -q)",
			f"{docker} image prune -f",
			f"{docker} container prune -f",
			f"{docker} builder prune -f -a"
	]

def base_run(dockerName, ports=[], flags="", detatched=False, mount="/sync", dind=False, cmd="/bin/bash"):
	if dind:
		if platform.system().lower() == "darwin":  #Mac
			dockerInDocker = "--privileged=true -v /private/var/run/docker.sock:/var/run/docker.sock"
		elif platform.system().lower() == "linux":
			dockerInDocker = "--privileged=true -v /var/run/docker.sock:/var/run/docker.sock"
	else:
		dockerInDocker = ""

	return f"{docker} run {dockerInDocker} --rm {'-d' if detatched else '-it'} -v \"{dir}:{mount}\" {getPort(ports)} {flags} {getDockerImage(dockerName)} {cmd}"

if __name__ == '__main__':
	args, cmds, execute = getArgs(), [], True
	regrun = lambda x:base_run(x, args.ports, "", args.detach, args.mount, args.dind, args.cmd)
	regcmd = lambda x,y:base_run(x, args.ports, "", args.detach, args.mount, args.dind, y)

	if args.command[0].strip() == "":
		print("No command specified")
		sys.exit(1)
	elif args.command[0] == "run":
		cmds += [
			regrun(args.docker[0])
		]
	elif args.command[0] == "wrap":
		cmds += [
			base_run(args.docker[0], ports, "", args.detach, args.mount, args.dind, args.cmd)
		] + clean()
	elif args.command[0] == "pylite":
		cmds += [
			regrun("frantzme/pythondev:lite")
		]
	elif args.command[0] == "writelite":
		cmds += [
			regrun("frantzme/writer:lite")
		]
	elif args.command[0] == "jlite":
		cmds += [
			regrun("frantzme/javadev:lite")
		]
	elif args.command[0] == "netdata" and False: #Need to figure out
		cmds += [
			base_run("netdata/netdata:latest", ['19999'], f"-v netdataconfig:/etc/netdata -v netdatalib:/var/lib/netdata -v netdatacache:/var/cache/netdata -v /etc/passwd:/host/etc/passwd:ro -v /etc/group:/host/etc/group:ro -v /proc:/host/proc:ro -v /sys:/host/sys:ro -v /etc/os-release:/host/etc/os-release:ro {'--restart unless-stopped' if args.detach else ''} --cap-add SYS_PTRACE --security-opt apparmor=unconfined", args.detach, args.mount, args.dind, "")
		]
	elif args.command[0] == "mypy":
		cmds += [
			regcmd("frantzme/pythondev:latest", "bash -c \"cd /sync && ipython3 --no-banner --no-confirm-exit --quick\"")
		]
	elif args.command[0] == "dive":
		#https://github.com/wagoodman/dive
		cmds += [
			f"{docker} pull {getDockerImage(args.docker[0])}",
			f"dive {getDockerImage(args.docker[0])}"
		]
	elif args.command[0] == "build":
		cmds = [
			f"{docker} build -t {args.name[0]} .",
			f"{docker} run --rm -it -v \"{dir}:/sync\" {args.name[0]} {args.cmd}"
		]
	elif args.command[0] == "lopy":
		cmds += [
			base_run("frantzme/pythondev:latest", [], "--env AUTHENTICATE_VIA_JUPYTER=\"password\"", args.detach, args.mount, args.dind, "bash -c \"cd /sync && ipython3 --no-banner --no-confirm-exit --quick -i {args.cmd} \"")
		]
	elif args.command[0] == "blockly":
		cmds += [
			base_run("frantzme/ml:latest", ["5000"], "--env AUTHENTICATE_VIA_JUPYTER=\"password\"", args.detach, args.mount, args.dind, "blockly")
		]
	elif args.command[0] == "mll":
		cmds += [
			base_run("dagshub/ml-workspace:latest", ["8080"], "--env AUTHENTICATE_VIA_JUPYTER=\"password\"", args.detach, args.mount, args.dind, "bash -c \"cd /sync && ipython3 --no-banner --no-confirm-exit --quick\"")
		]
	elif args.command[0] == "labpy":
		cmds += [
			base_run("frantzme/pythondev:latest", ["8888"], "--env AUTHENTICATE_VIA_JUPYTER=\"password\"", args.detach, args.mount, args.dind, "jupyter lab --ip=0.0.0.0 --allow-root --port 8888 --notebook-dir=\"/sync/\"")
		]
	elif args.command[0] == "jlab":
		cmds += [
			base_run("oneoffcoder/java-jupyter", ["8675"], None,None, args.mount, args.dind, f"jupyter lab --ip=0.0.0.0 --allow-root --port 8675 --notebook-dir=\"/sync/\"")
		]
	elif args.command[0] == "lab":
		cmds += [
			base_run("frantzme/pythondev:latest", ["8675"], None, None, args.mount, args.dind, f"jupyter lab --ip=0.0.0.0 --allow-root --port 8675 --notebook-dir=\"/sync/\"")
		]
	elif args.command[0] == "qodana-jvm":
		output_results = "qodana_jvm_results"
		try:
			os.system(f"mkdir {output_results}")
		except:
			pass

		cmds += [
			base_run("jetbrains/qodana-jvm", ["8080"], f"-v \"{output_results}:/data/results/\"  --show-report", "/data/project/", args.mount, args.dind, "/bin/bash")
		]
	elif args.command[0] == "qodana-py":
		cmds += [
			base_run("jetbrains/qodana-python:2022.1-eap", ["8080"], "--show-report", "/data/project/", args.mount, args.dind, "/bin/bash")
		]
	elif args.command[0] == "splunk":
		cmds += [
			base_run("splunk/splunk:latest", ["8000"], "-e SPLUNK_START_ARGS='--accept-license' -e SPLUNK_PASSWORD='password'",None, args.mount, args.dind, "/bin/bash")
		]
	elif args.command[0] == "beaker":
		cmds += [
			base_run("beakerx/beakerx", ["8888"], None, args.detach, args.mount, args.dind, "/bin/bash")
		]
	elif args.command[0] == "superset":
		cmds += [
			base_run("apache/superset:latest", ["8088"], None, args.detach, args.mount, args.dind, "/bin/bash")
		]
	elif args.command[0] == "mysql":
		cmds += [
			base_run("mysql:latest", ["3306"], "-e MYSQL_ROOT_PASSWORD=root", args.detach, args.mount, args.dind, "/bin/bash")
		]
	elif args.command[0] == "load":
		cmds += [
			f"{docker} pull {getDockerImage(args.docker[0])}"
		]
	elif args.command[0] == "clean":
		cmds += clean()
	elif args.command[0] == "stop":
		cmds += [f"{docker} kill $({docker} ps -a -q)"]
	elif args.command[0] == "list":
		cmds = [f"{docker} images"]
	elif args.command[0] == "live":
		cmds = [f"{docker} ps|awk '{{print $1, $3}}'"]
	elif args.command[0] == "update":
		containerID = run(f"{docker} ps |awk '{{print $1}}'|tail -1")
		imageID = run(f"{docker} ps |awk '{{print $2}}'|tail -1")

		cmds = [
			f"{docker} commit {containerID} {imageID}",
			f"{docker} push {imageID}"
		]		
	elif args.command[0] == "kill":
		if len(sys.argv) != 3:
			print("Please enter a docker name")
			sys.exit(0)

		dockerName = getDockerImage(sys.argv[2].strip()).replace(':latest', '')
		cmds = [
			f"{docker} kill $({docker} ps |grep {getDockerImage()}|awk '{{print $1}}')",
			f"{docker} rmi $(docker images |grep {dockerName}|awk '{{print $3}}')"
		]
	elif args.command[0] == "loads":
		for load in args.docker:
			cmds += [f"{docker} pull {getDockerImage(load)}"]

	for x in cmds:
		try:
			print(f"> {x}")
			if execute:
				os.system(x)
		except:
			pass

"""
	elif command == "push":
		if len(sys.argv) != 4:
			print(
				"Please enter the both the Docker Name and the running Docker ID"
			)
			sys.exit()

		dockerName = sys.argv[2].strip()
		dockerID = sys.argv[3].strip()
		cmds = [
			f"{docker} commit {dockerInDocker} {dockerID} {getDockerImage(dockerName)}",
			f"{docker} push {getDockerImage(dockerName)}"
		]
	elif command == "theia":
		if len(sys.argv) != 3:
			print("Please enter the Docker Name")
			sys.exit()
		dockerName = sys.argv[2].strip()
		#rest = 'bash -c "source /root/.bashrc && cd /Programs/theia/examples/browser && /root/.nvm/versions/node/v12.14.1/bin/yarn run start /sync --hostname 0.0.0.0"'
		base = "/root/.nvm/versions/node/v12.14.1/bin/yarn"
		if "py" in dockerName.lower():
			base = "/usr/local/bin/yarn"
		rest = f"bash -c \"cd /Programs/theia/examples/browser && {base} run start /sync --hostname 0.0.0.0\""

		dis_port = "3000"
		if not checkPort(dis_port):
			dis_port = open_port()

		ports = getPorts(ports=[f"3000:{dis_port}"])
		cmds = [
			f"{docker} run {dockerInDocker} --rm -it {ports} -v \"{dir}:/sync\" {getDockerImage(dockerName)} {rest}"
		]

	elif command == "cmd":
		if len(sys.argv) < 4:
			print("Please enter the both the Docker Name")
			sys.exit()

		dockerName = sys.argv[2].strip()
		ports = f"{getPorts()}" if sys.argv[3] == "port" else ""

		cmdRange = 4 if sys.argv[3] == "port" else 3
		rest = ' '.join(sys.argv[cmdRange:]).strip()
		if "lab" == rest.strip():
			dis_port = "8675"
			if not checkPort(dis_port):
				dis_port = open_port()

			rest = f"jupyter lab --ip=0.0.0.0 --allow-root --port {dis_port} --notebook-dir=\"/sync/\""
			ports = getPorts(ports=[f"{dis_port}:{dis_port}"])
		if "theia" == rest.strip():
			dis_port = "3000"
			if not checkPort(dis_port):
				dis_port = open_port()

			rest = "theia"
			ports = getPorts(ports=[f"{dis_port}:{dis_port}"])
		if "jekyll" == rest.strip():
			dis_port = "4000"
			if not checkPort(dis_port):
				dis_port = open_port()

			ports = getPorts(ports=[f"{dis_port}:{dis_port}"])

		rest = rest.replace("./", "/sync/")

		cmds = [
			f"{docker} run {dockerInDocker} --rm -it {ports} -v \"{dir}:/sync\" {getDockerImage(dockerName)} {rest}"
		]

	elif command == "telegram":
		cmds = [
			f"{docker} run -ti weibeld/ubuntu-telegram-cli bin/telegram-cli"
		]
"""