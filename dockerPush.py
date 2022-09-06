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

Eventually switch to
https://github.com/docker/docker-py

Things to add:
* Join existing and running docker container
"""

if False:
	try:
		import docker
	except:
		os.system(str(sys.executable) + " -m pip install docker")
		import docker

def is_docker():
	path = '/proc/self/cgroup'
	return (os.path.exists('/.dockerenv') or os.path.isfile(path) and
			any('docker' in line for line in open(path)))

docker = "docker"
docker_username = "frantzme"

'''####################################
#The main runner of this file, intended to be ran from
'''####################################

if False:
	class engine(object):
		def __init__(self, engineType):
			self.engineType = engineType #cmd or python
		
		def __get_port(self,port):
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			result = bool(sock.connect_ex(('127.0.0.1', int(port))))
			sock.close()

			if sock:
				return port
			else:
				sock = socket.socket()
				sock.bind(('', 0))
				x, port = sock.getsockname()
				sock.close()
				return port

		def __cmd(self,string):
			return str(subprocess.check_output(string, shell=True, text=True)).strip()

	

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

def getPort(ports=[], prefix="-p"):
	if ports is None or ports == []:
		return ''
	return ' '.join([
		f"{prefix} {port if checkPort(port) else open_port()}:{port}" for port in ports
	])

dir = '%cd%' if sys.platform in ['win32','cygwin'] else '`pwd`'

def getDockerImage(input):
	if "/" not in input:
		use_lite = ":lite" in input
		if "pydev" in input:
			output = f"{docker_username}/pythondev:latest"
		elif "pytest" in input:
			output = f"{docker_username}/pythontesting:latest"
		else:
			output = f"{docker_username}/{input}:latest"
		if use_lite:
			output = output.replace(':latest','') + ":lite"
		return output.replace(':latest:latest',':latest').replace(':lite:lite',':lite')
	else:
		return input

def getArgs():
	import argparse
	parser = argparse.ArgumentParser("Dcokerpush = useful utilities for running docker images")
	parser.add_argument("-x","--command", help="The Docker image to be used", nargs=1, default="clean")
	parser.add_argument("-d","--docker", help="The Docker image to be used", nargs='*', default="frantzme/pydev:latest")
	parser.add_argument("-p","--ports", help="The ports to be exposed", nargs="*", default=[])
	parser.add_argument("-c","--cmd", help="The cmd to be run", nargs="*", default=["/bin/bash"])
	parser.add_argument("--dind", help="Use Docker In Docker", action="store_true", default=False)
	parser.add_argument("--detach", help="Run the docker imagr detached", action="store_true",default=False)
	parser.add_argument("--shebang", help="", action="store_true",default=False)
	parser.add_argument("--mount", help="mount the current directory to which virtual folder",default="/sync")
	parser.add_argument("-n","--name", help="The name of the image",default="kinde")
	#args,unknown = parser.parse_known_args()
	args = parser.parse_args()
	return args 

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
		if False and platform.system().lower() == "darwin":  #Mac
			dockerInDocker = "--privileged=true -v /private/var/run/docker.sock:/var/run/docker.sock"
		else: #if platform.system().lower() == "linux":
			dockerInDocker = "--privileged=true -v /var/run/docker.sock:/var/run/docker.sock"
	else:
		dockerInDocker = ""

	if isinstance(cmd, list):
		cmd = ' '.join(cmd)

	return f"{docker} run {dockerInDocker} --rm {'-d' if detatched else '-it'} -v \"{dir}:{mount}\" {getPort(ports)} {flags or ''} {getDockerImage(dockerName)} {cmd or ''}"

def write_docker_compose(dockerName, ports=[], flags="", detatched=False, mount="/sync", dind=False, cmd="/bin/bash",name="kinde"):
	try:
		from yaml import load, dump,safe_load
	except:
		os.system(str(sys.executable)+" -m pip install pyyaml")
		from yaml import load, dump, safe_load
	
	try:
		from yaml import CLoader as Loader, CDumper as Dumper
	except ImportError:
		from yaml import Loader, Dumper
	from fileinput import FileInput as finput

	print(os.path.exists("docker-compose.yml"))

	if os.path.exists("docker-compose.yml"):
		with open("docker-compose.yml", "r") as writer:
			contents = safe_load(writer)
	else:
		contents = {
			'services': {}
		}
	
	contents['services'][name] = {
		'image': dockerName,
		'privileged':dind,
		'volumes': [
			'./:'+str(mount)
		],
	}

	if dind:
		contents['services'][name]['volumes'] += ['/var/run/docker.sock:/var/run/docker.sock']

	portz = [x for x in getPort(ports,prefix="").split(' ') if x.strip() != '']
	if len(portz) >0:
		contents['services'][name]['ports'] = portz

	if cmd[0] is not None and cmd[0] != "/bin/bash":
		contents['services'][name]['command'] = cmd[0]

	with open("docker-compose.yml", "w+") as writer:
		dump(contents, writer, default_flow_style=False)
	
	return "docker compose up " + str('-d' if detatched else '')

if __name__ == '__main__':
	if not os.path.exists('/usr/bin/docker'):
		os.system("yes|apt-get install docker.io")

	if '--shebang' in ''.join(sys.argv):
		sys.argv = ' '.join(sys.argv[:-1]).split(' ')
	args, cmds, execute = getArgs(), [], True
	regrun = lambda x:base_run(x, args.ports, "", args.detach, args.mount, args.dind, ' '.join(args.cmd))
	regcmd = lambda x,y:base_run(x, args.ports, "", args.detach, args.mount, args.dind, y)

	_cmd_string = str(args.command[0]).strip().lower()
	if _cmd_string.strip() == "":
		print("No command specified")
		sys.exit(1)
	if _cmd_string in ["clean","frun"]:
		cmds += clean()
	if _cmd_string == "update":
		try:
			import requests
		except:
			os.system(str(sys.executable) + " -m pip install requests")
			import requests
		from fileinput import FileInput as finput

		resp = requests.get("https://rebrand.ly/pydock")
		if resp.ok:
			with finput(__file__,inplace=True) as foil:
				for old_line in foil:
					for line in resp.text.split('\n'):
						print(line)
					break
	if _cmd_string == "pose":
		write_docker_compose(getDockerImage(args.docker[0]), args.ports, "", args.detach, args.mount, args.dind, args.cmd, args.name)
	if _cmd_string == "poser":
		cmds += [
			write_docker_compose(getDockerImage(args.docker[0]), args.ports, "", args.detach, args.mount, args.dind, args.cmd,args.name),
			"rm docker-compose.yml"
		]
	if _cmd_string in ["run","frun"]:
		cmds += [
			regrun(args.docker[0])
		]
	if _cmd_string == "wrap":
		cmds += [
			base_run(args.docker[0], args.ports, "", args.detach, args.mount, args.dind, args.cmd)
		] + clean()
	if _cmd_string == "pylite":
		cmds += [
			regrun("frantzme/pythondev:lite")
		]
	if _cmd_string == "writelite":
		cmds += [
			regrun("frantzme/writer:lite")
		]
	if _cmd_string == "jlite":
		cmds += [
			regrun("frantzme/javadev:lite")
		]
	if _cmd_string == "netdata" and False: #Need to figure out
		cmds += [
			base_run("netdata/netdata:latest", ['19999'], f"-v netdataconfig:/etc/netdata -v netdatalib:/var/lib/netdata -v netdatacache:/var/cache/netdata -v /etc/passwd:/host/etc/passwd:ro -v /etc/group:/host/etc/group:ro -v /proc:/host/proc:ro -v /sys:/host/sys:ro -v /etc/os-release:/host/etc/os-release:ro {'--restart unless-stopped' if args.detach else ''} --cap-add SYS_PTRACE --security-opt apparmor=unconfined", args.detach, args.mount, args.dind, "")
		]
	if _cmd_string == "mypy":
		cmds += [
			regcmd("frantzme/pythondev:latest", "bash -c \"cd /sync && ipython3 --no-banner --no-confirm-exit --quick\"")
		]
	if _cmd_string == "dive":
		#https://github.com/wagoodman/dive
		cmds += [
			f"{docker} pull {getDockerImage(args.docker[0])}",
			f"dive {getDockerImage(args.docker[0])}"
		]
	if _cmd_string == "build":
		cmds = [
			f"{docker} build -t {args.name[0]} .",
			f"{docker} run --rm -it -v \"{dir}:/sync\" {args.name[0]} {args.cmd}"
		]
	if _cmd_string == "lopy":
		cmds += [
			base_run("frantzme/pythondev:latest", [], "--env AUTHENTICATE_VIA_JUPYTER=\"password\"", args.detach, args.mount, args.dind, "bash -c \"cd /sync && ipython3 --no-banner --no-confirm-exit --quick -i {args.cmd} \"")
		]
	if _cmd_string == "blockly":
		cmds += [
			base_run("frantzme/ml:latest", ["5000"], "--env AUTHENTICATE_VIA_JUPYTER=\"password\"", args.detach, args.mount, args.dind, "blockly")
		]
	if _cmd_string == "mll":
		cmds += [
			base_run("dagshub/ml-workspace:latest", ["8080"], "--env AUTHENTICATE_VIA_JUPYTER=\"password\"", args.detach, args.mount, args.dind, "bash -c \"cd /sync && ipython3 --no-banner --no-confirm-exit --quick\"")
		]
	if _cmd_string == "labpy":
		cmds += [
			base_run("frantzme/pythondev:latest", ["8888"], "--env AUTHENTICATE_VIA_JUPYTER=\"password\"", args.detach, args.mount, args.dind, "jupyter lab --ip=0.0.0.0 --allow-root --port 8888 --notebook-dir=\"/sync/\"")
		]
	if _cmd_string == "jlab":
		cmds += [
			base_run("oneoffcoder/java-jupyter", ["8675"], None,None, args.mount, args.dind, f"jupyter lab --ip=0.0.0.0 --allow-root --port 8675 --notebook-dir=\"/sync/\"")
		]
	if _cmd_string == "lab":
		cmds += [
			base_run("frantzme/pythondev:latest", ["8675"], None, None, args.mount, args.dind, f"jupyter lab --ip=0.0.0.0 --allow-root --port 8675 --notebook-dir=\"/sync/\"")
		]
	if _cmd_string == "sos":
		cmds += [
			base_run("vatlab/sos-notebook", ["8678"], None, None, "/home/jovyan/work", args.dind, f"jupyter lab --ip=0.0.0.0 --allow-root --port 8678")
		]
	if _cmd_string == "polynote":
		#https://github.com/polynote/polynote/blob/master/docker/README.md
		cmds += [
			base_run("polynote/polynote:latest", ["8192"], None, None, "data", args.dind, f"-p 127.0.0.1:8192:8192 -p 127.0.0.1:4040-4050:4040-4050")
		]
	if _cmd_string == "polynote2":
		cmds += [
			base_run("xtreamsrl/polynote-docker", ["8192"],None, args.detach,"/data", args.dind, args.cmd)
		]
	if _cmd_string == "cmd":
		cmds += [
			base_run(args.docker[0], args.ports, None, None, args.mount, args.dind, ' '.join(args.cmd))
		]
	if _cmd_string == "qodana-jvm":
		output_results = "qodana_jvm_results"
		try:
			os.system(f"mkdir {output_results}")
		except:
			pass

		cmds += [
			base_run("jetbrains/qodana-jvm", ["8080"], f"-v \"{output_results}:/data/results/\"  --show-report", "/data/project/", args.mount, args.dind, "/bin/bash")
		]
	if _cmd_string == "qodana-py":
		cmds += [
			base_run("jetbrains/qodana-python:2022.1-eap", ["8080"], "--show-report", "/data/project/", args.mount, args.dind, "/bin/bash")
		]
	if _cmd_string == "splunk":
		cmds += [
			base_run("splunk/splunk:latest", ["8000"], "-e SPLUNK_START_ARGS='--accept-license' -e SPLUNK_PASSWORD='password'",None, args.mount, args.dind, "start")
		]
	if _cmd_string == "beaker":
		cmds += [
			base_run("beakerx/beakerx", ["8888"], None, args.detach, args.mount, args.dind, "/bin/bash")
		]
	if _cmd_string == "superset":
		cmds += [
			base_run("apache/superset:latest", ["8088"], None, args.detach, args.mount, args.dind, "/bin/bash")
		]
	if _cmd_string == "mysql":
		cmds += [
			base_run("mysql:latest", ["3306"], "-e MYSQL_ROOT_PASSWORD=root", args.detach, args.mount, args.dind, "/bin/bash")
		]
	if _cmd_string in ["load","pull"]:
		cmds += [
			f"{docker} pull {getDockerImage(args.docker[0])}"
		]
	if _cmd_string in ["clean"]:
		cmds += clean()
	if _cmd_string == "stop":
		cmds += [f"{docker} kill $({docker} ps -a -q)"]
	if _cmd_string == "list":
		cmds = [f"{docker} images"]
	if _cmd_string == "live":
		cmds = [f"{docker} ps|awk '{{print $1, $3}}'"]
	if _cmd_string == "update":
		containerID = run(f"{docker} ps |awk '{{print $1}}'|tail -1")
		imageID = run(f"{docker} ps |awk '{{print $2}}'|tail -1")

		cmds = [
			f"{docker} commit {containerID} {imageID}",
			f"{docker} push {imageID}"
		]		
	if _cmd_string == "kill":
		if len(sys.argv) != 3:
			print("Please enter a docker name")
			sys.exit(0)

		dockerName = getDockerImage(sys.argv[2].strip()).replace(':latest', '')
		cmds = [
			f"{docker} kill $({docker} ps |grep {getDockerImage()}|awk '{{print $1}}')",
			f"{docker} rmi $(docker images |grep {dockerName}|awk '{{print $3}}')"
		]
	if _cmd_string in ["loads","pulls"]:
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
