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
import shlex
import platform
import pwd
import socket
import argparse

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


def user():
	return str(pwd.getpwuid(os.getuid())[0])


docker = "docker"
docker_username = "frantzme"

'''####################################
#The main runner of this file, intended to be ran from
'''####################################


def run(cmd):
	return str(subprocess.check_output(cmd, shell=True, text=True)).strip()


loaded = [
]


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


def getPorts(prefix="-p", ports=None):
	output = ""
	if ports is None:
		ports = []
		for i in range(1):
			dis_port = open_port()
			ports += [f"{dis_port}:{dis_port}"]

	for port in ports:
		output = f"{output} {prefix} {port}"
	return output


def getDockerImage(input):
	if "/" not in input:
		if "pydev" in input:
			output = f"{docker_username}/pythondev:latest"
		elif "pytest" in input:
			output = f"{docker_username}/pytesting:latest"
		else:
			output = f"{docker_username}/{input}:latest"
		return output
	else:
		return input


if __name__ == '__main__':
	command = sys.argv[1].strip().lower()
	dockerName = None
	dockerID = None
	execute = True
	dockerInDocker = ""
	if command.startswith(":"):
		command = command.replace(':', '')
		current_user = user()

		if platform.system().lower() == "darwin":  #Mac
			#dockerInDocker = f"--privileged=true -v /Users/{current_user}/.docker/run/docker.sock:/var/run/docker.sock"
			dockerInDocker = f"--privileged=true -v /private/var/run/docker.sock:/var/run/docker.sock"
		elif platform.system().lower() == "linux":
			dockerInDocker = f"--privileged=true -v /var/run/docker.sock:/var/run/docker.sock"

	cmds = []
	if command == "push":
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
	elif command == "run":
		if len(sys.argv) != 3 and len(sys.argv) != 4:
			print("Please enter the both the Docker Name")
			sys.exit()

		dockerName = sys.argv[2].strip()
		ports = f"{getPorts()}" if len(
			sys.argv) == 4 and sys.argv[3] == "port" else ""
		cmds = [
			f"{docker} run {dockerInDocker} --rm -it {ports} -v \"`pwd`:/sync\" {getDockerImage(dockerName)}"
		]
	elif command == "rep":
		if len(sys.argv) != 3:
			print("Please enter the both the Docker Name")
			sys.exit()

		dockerName = sys.argv[2].strip()
		cmds = [
			f"{docker} kill $({docker} ps -q)",
			f"{docker} rm $({docker} ps -a -q)",
			f"{docker} rmi $({docker} images -q)",
			f"{docker} run {dockerInDocker} --rm -it -v \"`pwd`:/sync\" {getDockerImage(dockerName)}"
		]
	elif command == "wrap":
		if len(sys.argv) != 3 and len(sys.argv) != 4:
			print("Please enter the both the Docker Name")
			sys.exit()

		dockerName = sys.argv[2].strip()
		ports = f"{getPorts()}" if len(
			sys.argv) == 4 and sys.argv[3] == "port" else ""
		cmds = [
			f"{docker} run {dockerInDocker} --rm -it {ports} -v \"`pwd`:/sync\" {getDockerImage(dockerName)}",
			f"{docker} kill $({docker} ps -q)",
			f"{docker} rm $({docker} ps -a -q)",
			f"{docker} rmi $({docker} images -q)"
		]
	elif command == "mypy":
		dockerName = "pydev"

		cmds = [
			f"{docker} run {dockerInDocker} --rm -it -v \"`pwd`:/sync\" {getDockerImage(dockerName)} bash -c \"cd /sync && ipython3 --no-banner --no-confirm-exit --quick\""
		]
	elif command == "lopy":
		dockerName = "pydev"

		rest = ' '.join(sys.argv).split("lopy")[-1]

		cmds = [
			f"{docker} run {dockerInDocker} --rm -it -v \"`pwd`:/sync\" {getDockerImage(dockerName)} bash -c \"cd /sync && ipython3 --no-banner --no-confirm-exit --quick -i {rest} \""
		]
	elif command == "blockly":
		dockerName = "ml"

		dis_port = "5000"
		if not checkPort(dis_port):
			dis_port = open_port()
		ports = getPorts(ports=[f"{dis_port}:{dis_port}"])

		cmds = [
			f"{docker} run {dockerInDocker} --rm -it {ports} -v \"`pwd`:/sync\" {getDockerImage(dockerName)} blockly"
		]
	elif command == "python" or command == "py":
		if len(sys.argv) != 3:
			print("Please enter the Docker Name")
			sys.exit()
		dockerName = sys.argv[2].strip()

		cmds = [
			f"{docker} run {dockerInDocker} --rm -it -v \"`pwd`:/sync\" {getDockerImage(dockerName)} ipython3"
		]
	elif command == "labpy":
		dockerName = "pydev"

		dis_port = "8675"
		if not checkPort(dis_port):
			dis_port = open_port()

		rest = f"jupyter lab --ip=0.0.0.0 --allow-root --port {dis_port} --notebook-dir=\"/sync/\""
		ports = getPorts(ports=[f"{dis_port}:{dis_port}"])
		cmds = [
			f"{docker} run {dockerInDocker} --rm -it {ports} -v \"`pwd`:/sync\" {getDockerImage(dockerName)} {rest}"
		]
	elif command == "jlab":
		dockerName = "pydev"

		dis_port = "8675"
		if not checkPort(dis_port):
			dis_port = open_port()

		#rest = f"jupyter lab --ip=0.0.0.0 --allow-root --port {dis_port} --notebook-dir=\"/sync/\""
		rest = f"jupyter lab --ip=0.0.0.0 --allow-root --port {dis_port} --notebook-dir=\"/sync/\""
		ports = getPorts(ports=[f"{dis_port}:{dis_port}"])
		cmds = [
			f"{docker} run {dockerInDocker} --rm -it {ports} -v \"`pwd`:/sync\" oneoffcoder/java-jupyter {rest}"# deepjavalibrary/jupyter {rest}"
		]
	elif command == "lab":
		if len(sys.argv) != 3:
			print("Please enter the Docker Name")
			sys.exit()
		dockerName = sys.argv[2].strip()

		dis_port = "8675"
		if not checkPort(dis_port):
			dis_port = open_port()

		rest = f"jupyter lab --ip=0.0.0.0 --allow-root --port {dis_port} --notebook-dir=\"/sync/\""
		ports = getPorts(ports=[f"{dis_port}:{dis_port}"])
		cmds = [
			f"{docker} run {dockerInDocker} --rm -it {ports} -v \"`pwd`:/sync\" {getDockerImage(dockerName)} {rest}"
		]
	elif command == "splunk":
		dis_port = "8000"
		if not checkPort(dis_port):
			dis_port = open_port()

		ports = getPorts(ports=[f"{dis_port}:8000"])
		cmds = [
			f"docker run {ports} -v \"`pwd`:/sync\" -e SPLUNK_START_ARGS='--accept-license' -e SPLUNK_PASSWORD='password' -v \"`pwd`:/sync\" splunk/splunk:latest"
		]
	elif command == "beaker":
		dis_port = "8888"
		if not checkPort(dis_port):
			dis_port = open_port()

		ports = getPorts(ports=[f"{dis_port}:8888"])
		cmds = [
			f"docker run {ports} -v \"`pwd`:/sync\" -v \"`pwd`:/sync\" beakerx/beakerx"
		]
	elif command == "superset":
		dis_port = "8088"
		if not checkPort(dis_port):
			dis_port = open_port()

		ports = getPorts(ports=[f"{dis_port}:8088"])
		cmds = [
			f"docker run {ports} -it -v \"`pwd`:/sync\" apache/superset:latest"
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
			f"{docker} run {dockerInDocker} --rm -it {ports} -v \"`pwd`:/sync\" {getDockerImage(dockerName)} {rest}"
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
			f"{docker} run {dockerInDocker} --rm -it {ports} -v \"`pwd`:/sync\" {getDockerImage(dockerName)} {rest}"
		]
	elif command == "mysql":
		cmds = [
			f"docker run --rm -it --name root  -p 3306:3306  -e MYSQL_ROOT_PASSWORD=root  mysql:latest"
		]
	elif command == "load":
		if len(sys.argv) != 3:
			print("Please enter the Docker Name")
			sys.exit()

		dockerName = sys.argv[2].strip()
		cmds += [f"{docker} pull {getDockerImage(dockerName)}"]
	elif command == "loads":
		for load in loaded:
			cmds += [f"{docker} pull {getDockerImage(load)}"]
	elif command == "loading":
		loaded = sys.argv[2:]

		for load in loaded:
			cmds += [f"{docker} pull {getDockerImage(load)}"]
	elif command == "clean":
		cmds = [
			f"{docker} kill $({docker} ps -a -q)",
			f"{docker} kill $({docker} ps -q)",
			f"{docker} rm $({docker} ps -a -q)",
			f"{docker} rmi $({docker} images -q)",
			f"docker volume rm $(docker volume ls -q)",
			f"{docker} image prune -f",
			f"{docker} container prune -f",
			f"{docker} builder prune -f -a"
		]
	elif command == "stop":
		cmds = [f"{docker} kill $({docker} ps -a -q)"]
	elif command == "list":
		cmds = [f"{docker} images"]
	elif command == "live":
		cmds = [f"{docker} ps|awk '{{print $1, $3}}'"]
	elif command == "update":
		containerID = run(f"docker ps |awk '{{print $1}}'|tail -1")
		imageID = run(f"docker ps |awk '{{print $2}}'|tail -1")

		cmds = [
			f"{docker} commit {containerID} {imageID}",
			f"{docker} push {imageID}"
		]
	elif command == "wrapthis":
		if len(sys.argv) != 3 and len(sys.argv) != 4:
			print("Please enter the both the Docker Name")
			sys.exit()

		dockerName = getDockerImage(sys.argv[2].strip())
		dockerNameTwo = dockerName.replace(':latest', '')
		ports = f"{getPorts()}" if len(
			sys.argv) == 4 and sys.argv[3] == "port" else ""
		cmds = [
			f"{docker} run {dockerInDocker} --rm -it {ports} -v \"`pwd`:/sync\" {dockerName}",
			f"{docker} kill $({docker} ps |grep {dockerNameTwo}|awk '{{print $1}}')",
			f"{docker} rmi $(docker images |grep {dockerNameTwo}|awk '{{print $3}}')"
		]
	elif command == "kill":
		if len(sys.argv) != 3:
			print("Please enter a docker name")
			sys.exit(0)

		dockerName = getDockerImage(sys.argv[2].strip()).replace(':latest', '')
		cmds = [
			f"{docker} kill $({docker} ps |grep {dockerName}|awk '{{print $1}}')",
			f"{docker} rmi $(docker images |grep {dockerName}|awk '{{print $3}}')"
		]
	elif command == "telegram":
		cmds = [
			f"{docker} run -ti weibeld/ubuntu-telegram-cli bin/telegram-cli"
		]

	for x in cmds:
		try:
			print(f"> {x}")
			if execute:
				os.system(x)
		except:
			pass
