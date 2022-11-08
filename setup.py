#!/usr/bin/env python3
# region Imports
import pathlib, zipfile
from fileinput import FileInput as finput
import os
import sys
from setuptools import find_packages, setup
from pathlib import Path
import glob
from glob import glob as re
try:
	from pylint.reporters.json_reporter import JSONReporter
except:
	pass


# endregion
# region Basic Information
here = os.path.abspath(os.path.dirname(__file__))
py_version = sys.version_info[:2]
NAME = "funbelts"
AUTHOR = 'Miles Frantz'
EMAIL = 'frantzme@vt.edu'
DESCRIPTION = 'My short description for my project.'
GH_NAME = "franceme"
URL = f"https://github.com/{GH_NAME}/{NAME}"
long_description = pathlib.Path(f"{here}/README.md").read_text(encoding='utf-8')
REQUIRES_PYTHON = '>=3.8.0'
RELEASE = "?"
entry_point = f"{NAME}.{NAME}"
VERSION = "0.1.62"

def grab_version(update_patch:bool=False,update_minor:bool=False,update_major:bool=False):
	update = any([update_patch,update_minor,update_major])
	with finput(__file__,inplace=True) as foil:
		for line in foil:
			if line.startswith("VERSION = "):
				output = line.strip().replace('VERSION = ','').replace('"','').split('.')
				major,minor,patch = int(output[0]),int(output[1]),int(output[2])

				if update_patch:
					patch += 1
				if update_minor:
					minor += 1
				if update_major:
					major += 1

				if update:
					print(f"VERSION = \"{major}.{minor}.{patch}\"")
				else:
					print(line,end='')

			else:
				print(line, end='')
	return

# endregion
# region CMD Line Usage
def selfArg(string):
	return __name__ == "__main__" and len(
		sys.argv) > 1 and sys.argv[0].endswith('/setup.py') and str(
			sys.argv[1]).upper() == str(string).upper()

if selfArg('install'):
	sys.exit(os.system('python3 -m pip install -e .'))
elif selfArg('patch'):
	grab_version(True)
	sys.exit(0)
elif selfArg('upload'):
	grab_version(True)
	sys.exit(os.system(f"{sys.executable} setup.py sdist && {sys.executable} -m twine upload --skip-existing dist/*"))
# endregion
# region Setup

setup(
	name=NAME,
	version=VERSION,
	description=DESCRIPTION,
	long_description=long_description,
	long_description_content_type='text/markdown',
	author=AUTHOR,
	author_email=EMAIL,
	command_options={
	},
	python_requires=REQUIRES_PYTHON,
	url=URL,
	packages=find_packages(
		exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
	entry_points={
	},
	install_requires=[
		"pandas",
		"sqlalchemy",
		"xlsxwriter",
		"psutil",
		"httplib2",
		"python-telegram-bot",
		"PyGithub",
        "rich",
        "waybackpy",
        "requests",
        "matplotlib",
		"ticktick-py" #https://github.com/lazeroffmichael/ticktick-py
	],
	include_package_data=True,
	classifiers=[
		'Programming Language :: Python',
		'Programming Language :: Python :: 3',
		'Programming Language :: Python :: 3.8',
	],
)
# endregion
