#!/usr/bin/python3

import os,sys,shelve


if __name__ == '__main__':
	self_name = str(__file__).replace('./','').lower()
	args = [x for x in set(map(lambda x: x.strip(), sys.argv)) if self_name not in x.lower()]

    if args == []:
        shelf_name = "output.shelf"
    else:
        shelf_name = args[0]

    with shelve.open(shelf_name, 'n') as shelf:
        for key in dir():
            try:
                shelf[key] = globals()[key]
            except TypeError:
                print(f"Could not shelf {key} due to type error")
            except Exception as e:
                print(f"Could not shelf {key} due to exception {e}")
    print("Completed")
