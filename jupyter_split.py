#!/usr/bin/python3

import os,sys,json

if __name__ == '__main__':
	self_name = str(__file__).replace('./','').lower()
	cmd, args = [], [x for x in set(map(lambda x: x.strip(), sys.argv)) if self_name not in x.lower()]

	if "clean" in args:
		os.system("rm *_SPLIT_*")
		sys.exit(0)

	foil = args[0]

	foil_name = foil.replace('.ipynb','')
	new_file_counter = 0

	with open(args[0],"r") as jupyter:
		contents = json.load(jupyter)

	len_cells = len(str(len(contents['cells'])))
	for cell in contents['cells']:
		if cell['cell_type'] == 'code':
			new_number = str(new_file_counter).zfill(int(len_cells))
			new_name,new_file_counter = f"{str(new_number)}_SPLIT_{foil_name}.py",new_file_counter+1
			with open(new_name,"w+") as writer:
				for line in cell['source']:

					if line.startswith('!'):
						line = 'os.system(f"' + line.replace("!",'').strip() + '")\n'

					writer.write(line)
