#!/usr/bin/env python3
import os,sys,fileinput

def contents(foil_name:str):
    with open("Makefile","w+") as writer:
        writer.write(f"""
file={foil_name}
hash_algo=sha512sum
hash=$(file).sums
default:: build
size=2G
#build: hash split
build: join

hash:
  @echo Creating a hash 512 of the file
  @$(hash_algo) $(file) >> $(hash)

verify:
  @echo Verifying the sums file
  @$(hash_algo) -c $(hash)

split:
  @echo Splitting the original file
  @split -b $(size) --verbose $(file) split_file_
  @echo Zipping files
  @for f in split_file_*;do echo $$f;7z a $$f.zip $$f -sdel -mx=0;done

join:
  @echo Unzipping files
  @for f in split_file_*zip;do echo $$f;7z x $$f;done
  @echo Removing all of the *.zip files
  @rm split_file_*zip
  @echo Joining the files
  @cat split_file_* > $(file)
  @echo Removing the split files
  @rm split_file_*
  @echo Checking the hash file
  @$(hash_algo) -c $(hash)
  @Removing the extra files
  @rm $(file)
  @rm $(hash)
  @rm Makefile
""")
    for line in fileinput.FileInput("Makefile",inplace=1):
        print(line.replace("  ","	"),end='')


def exe(cmd:str,exe:bool=True):
    try:
        print(cmd);
        if exe:
            os.system(cmd)
    except:
        pass

def main(args):
    big_file = str(args[0])
    args = list(map( lambda x:x.upper(), args[1:] ))
    if os.path.exists(big_file):
        naem = big_file.replace('.','_')
        exe(f"mkdir {naem}")
        exe(f"cp {big_file} {naem}")
        os.chdir(naem)
        contents(big_file)
        exe("make hash split")

if __name__ == '__main__':
    sys.exit(main( sys.argv[1:]  ))
