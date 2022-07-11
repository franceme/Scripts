#!/usr/bin/env python3
import os, sys, shutil
import subprocess,signal
from fileinput import FileInput as finput

file_ending, command, image, backupfile = ".tex","tectonic", "writer", None

def clear(signum,frame):
    global backupfile
    for remove in [backupfile]:
        if remove is not None and os.path.exists(remove):
            try:
                cmd = f"yes 2>/dev/null |rm -r {remove}"
                os.system(cmd)
            except:
                pass

signal.signal(signal.SIGINT,clear)


if __name__ == '__main__':
    if '-h' in ' '.join(sys.argv):
        print(f"""{__file__} ./file.{file_ending} or {__file__} file.{file_ending}

The file.{file_ending} needs to have the following two lines at the top.
#!/bin/sh
exec docker run  --rm -it  -v "`pwd`:/sync" frantzme/{image}:latest single_run $0
""")

    add, dir_name, working_file = False, None, None
    for arg in sys.argv:
        if arg.endswith(file_ending):
            working_file = arg.replace('./','')
            
            if arg.startswith('./'):
                working_file = "/sync/"+working_file
            backupfile = working_file+".back"

            shutil.copy(working_file, backupfile)
            with finput(working_file, inplace=True) as foil:
                look_for = False
                for itr,line in enumerate(foil):
                    clean = True
                    if itr == 0 and line.strip() == '#!/bin/sh':
                        look_for = True
                        clean = False
                    elif look_for and itr == 1 and line.strip().startswith('exec'):
                        clean = False
                        look_for = False

                    if clean:
                        print(line,end='')

            break

    if working_file is not None:
        cmd = f"{command} {os.path.abspath(working_file)}"
        print(cmd);
        process = subprocess.Popen(cmd,shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,bufsize=1,encoding='utf-8', universal_newlines=True, close_fds=True)
        while True:
            out = process.stdout.readline()
            if out == '' and process.poll() != None:
                break
            if out != '':
                sys.stdout.write(out)
                sys.stdout.flush()
        shutil.move(backupfile, working_file)
        clear(None,None)
