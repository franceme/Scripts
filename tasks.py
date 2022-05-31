#!/usr/bin/env python3
import os,sys

if __name__ == "__main__":
	os.system(f"{sys.executable} -m pip install --upgrade invoke funbelts")
	if os.path.exists("~/.bashrc"):
		with open("~/.bashrc", "a") as appender:
			appender.write("alias voke=invoke")
	sys.exit(0)

from invoke import task
import funbelts as ut

@task
def load(c):
	print("Starting")
	print("Loaded")
	return True

@task
def clean(c):
	return True
