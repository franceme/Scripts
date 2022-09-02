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

@task
def gitr(c):
	for x in [
		'git config --global user.email "EMAIL"',
		'git config --global user.name "UserName (pythondev@lite)"'
	]:
		print(x);os.system(x)

@task
def cleanenv(c):
	for x in [
		'CachedExtensions/',
		'CachedExtensionVSIXs/',
		'User/',
		'Machine/',
		'extensions/',
		'logs/',
		'coder.json',
		'machineid',
	]:
		x = "yes|rm -r " + str(x)
		print(x);os.system(x)

@task
def execute(c):
	print("Executing")
