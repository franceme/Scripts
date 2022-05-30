#!/usr/bin/env python3
import os,sys

if __name__ == "__main__":
	os.system(f"{sys.executable} -m pip install --upgrade invoke funbelts")
	return

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