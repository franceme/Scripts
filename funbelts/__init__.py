from __future__ import print_function
import os, sys, pwd, json, pandas as pd, numpy as np, sqlite3, pwd, uuid, platform, re, base64, string,enum,shelve
import matplotlib as mpl
import matplotlib.cm
import requests
from datetime import datetime as timr
from rich import print as outy
from sqlite3 import connect
from glob import glob
from copy import deepcopy as dc
import functools
from zlib import compress
import httplib2
import six
from waybackpy import WaybackMachineSaveAPI as checkpoint
from threading import Thread, Lock
from six.moves.urllib.parse import urlencode
if six.PY2:
    from string import maketrans
else:
    maketrans = bytes.maketrans
from difflib import SequenceMatcher

from sqlalchemy import create_engine
import pandas as pd
import psutil
import time
from telegram import Update, ForceReply, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext
from github import Github
import base64
import datasets
import hashlib
try:
    from cryptography.fernet import Fernet
except:
    os.system(str(sys.executable) + " -m pip install cryptography")
    from cryptography.fernet import Fernet

def is_docker():
	path = '/proc/self/cgroup'
	return (os.path.exists('/.dockerenv') or os.path.isfile(path) and
			any('docker' in line for line in open(path)))

def open_port():
	"""
	https://gist.github.com/jdavis/4040223
	"""
	sock = socket.socket()
	sock.bind(('', 0))
	x, port = sock.getsockname()
	sock.close()

	return port

def hash(file,hashfunc=hashlib.sha512()):
	with open(file,'rb') as f:
		while True:
			data = f.read(65536)
			if not data:
				break
			hashfunc.update(data)
	return str(hashfunc.hexdigest())

def hash_compare(file,hash,hashfunc=hashlib.sha512()):
    return str(hash) == hash(file=file,hashfunc=hashfunc)

def checkPort(port):
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	result = bool(sock.connect_ex(('127.0.0.1', int(port))))
	sock.close()
	return result

def flatten_list(lyst: list) -> list:
    if not lyst:
        return []

    big_list = len(lyst) > 1
    if isinstance(lyst[0], list):
        return flatten_list(lyst[0]) + (big_list * flatten_list(lyst[1:]))
    else:
        return [lyst[0]] + (big_list * flatten_list(lyst[1:]))

def json_set_check(obj):
    """
    json.dump(X,default=json_set_check)
    https://stackoverflow.com/questions/22281059/set-object-is-not-json-serializable
    """
    if isinstance(obj, set):
        return list(obj)
    raise TypeError

class Rollr(object):
    def __init__(self):
        self.tag = None
    def __enter__(self):
        print("[",end='',flush=True)
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        print("]")
        return self
    def step(self):
        print(".",end='',flush=True)

def live_link(url:str):
    response = False
    try:
        response_type = requests.get(url)
        response = response_type.status_code < 400
        time.sleep(2)
    except:
        pass
    return response

def save_link(url:str):
    save_url = None
    if live_link(url):
        saver = checkpoint(url, user_agent="Mozilla/5.0 (Windows NT 5.1; rv:40.0) Gecko/20100101 Firefox/40.0")
        try:
            save_url = saver.save()
            time.sleep(10)
            if save_url is None:
                save_url = saver.saved_archive
        except Exception as e:
            print(f"Issue with saving the link {url}: {e}")
            pass
    return save_url

def zip_from_archive(url:str, file_name:str="tmp.zip"):
    if not file_name.endswith(".zip"):
        file_name += ".zip"

    if "web.archive.org" in url and live_link(url):
        try:
            new_url = url.replace('/https://','if_/https://')
            req = requests.get(new_url)
            open(file_name,"wb").write(req.content)
        except Exception as e:
            print(f"Exception :> {e}")

    return file_name


def str_to_base64(string, password:bool=False, encoding:str='utf-8'):
    current = base64.b64encode(string.encode(encoding))
    if password:
        key = Fernet.generate_key()
        current = Fernet(key).encrypt(current)
        key = key.decode(encoding)
    return (current.decode(encoding), key or None)

def base64_to_str(b64, password:str=None, encoding:str='utf-8'):
     if password:
         current = Fernet(password.encode(encoding)).decrypt(b64.encode(encoding)).decode(encoding)
     return base64.b64decode(current or b64).decode(encoding)

def silent_exec(default=None, returnException:bool=False):
    """
    https://stackoverflow.com/questions/39905390/how-to-auto-wrap-function-call-in-try-catch

    Usage: @silent_exec()
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                return e if returnException else default
        return wrapper
    return decorator

def write_shelf(shelf_name, print_out:bool=False):
    with shelve.open(shelf_name, 'n') as shelf:
        for key in dir():
            try:
                shelf[key] = globals()[key]
            except TypeError:
                print(f"Error shelving the key {key} due to a type error")
            except Exception as e:
                print(f"Error shelving the key {key} due to {e}")

    if print_out:
        print(f"The shelf has been written")

def load_shelf(shelf_name, print_out:bool=False):
    with shelve.open(shelf_name) as shelf:
        for key in shelf:
            if print_out:
                print(f"Loading the shelf item {key}")
            globals()[key] = shelf[key]

    if print_out:
        print(f"The shelf has been loaded")

def install_import(importname):
    os.system(f"{sys.executable} -m pip install {importname} --upgrade")

def user():
    return str(pwd.getpwuid(os.getuid())[0]).strip().lower()

percent = lambda x,y: ("{0:.2f}").format(100 * (x / float(y)))
cur_time = str(timr.now().strftime('%Y_%m_%d-%H_%M'))
rnd = lambda _input: f"{round(_input * 100)} %"
similar = lambda x,y:SequenceMatcher(None, a, b).ratio()*100
file_by_type = lambda PATH,ext:[os.path.join(dp, f) for dp, dn, filenames in os.walk(PATH) for f in filenames if os.path.splitext(f)[1] == ext]
file_by_name = lambda PATH,name:[os.path.join(dp, f) for dp, dn, filenames in os.walk(PATH) for f in filenames if f == name]
of_dir = lambda PATH,name:[os.path.join(dp, f) for dp, dn, filenames in os.walk(PATH) for f in filenames if os.path.isdir(f) and f == name]

def metrics(TP,FP,TN,FN, use_percent:bool=False):
    div = lambda x,y:x/y if y else 0
    prep = lambda x:percent(x, 100) if use_percent else x
    precision, recall = div(TP , (TP + FP)), div(TP , (TP + FN))

    return {
        'TP': TP,
        'FP': FP,
        'TN': TN,
        'FN': FN,
        'Precision_PPV': prep(precision),
        'Recall': prep(recall),
        'Specificity_TNR': prep(div(TN , (TN + FP))),
        'FNR': prep(div(FN , (FN + TP))),
        'FPR': prep(div(FP , (FP + TN))),
        'FDR': prep(div(FP , (FP + TP))),
        'FOR': prep(div(FN , (FN + TN))),
        'TS': prep(div(TP , (TP + FN + FP))),
        'Accuracy': prep(div((TP + TN) , (TP + TN + FP + FN))),
        'PPCR': prep(div((TP + FP) , (TP + TN + FP + FN))),
        'F1': prep(2 * div( (precision * recall),(precision + recall) )),
    }

def add_metrics(fwame, TP:str='TP',FP:str='FP',TN:str='TN',FN:str='FN', use_percent:bool=False):
    div = lambda x,y:x/y if y else 0
    prep = lambda x:percent(x, 100) if use_percent else x

    fwame['Precision_PPV'] = prep(fwame[TP]/(fwame[TP]+fwame[FP]))
    fwame['Recall'] = prep(fwame[TP]/(fwame[TP]+fwame[FN]))
    fwame['Specificity_TNR'] = prep(fwame[TN]/(fwame[TN]+fwame[FP]))
    fwame['FNR'] = prep(fwame[FN]/(fwame[FN]+fwame[TP]))
    fwame['FPR'] = prep(fwame[FP]/(fwame[FP]+fwame[TN]))
    fwame['FDR'] = prep(fwame[FP]/(fwame[FP]+fwame[TP]))
    fwame['FOR'] = prep(fwame[FN]/(fwame[FN]+fwame[TN]))
    fwame['TS'] = prep(fwame[TP]/(fwame[TP]+fwame[FP]+fwame[FN]))
    fwame['Accuracy'] = prep((fwame[TP]+fwame[TN])/(fwame[TP]+fwame[FP]+fwame[TN]+fwame[FN]))
    fwame['PPCR'] = prep((fwame[TP]+fwame[FP])/(fwame[TP]+fwame[FP]+fwame[TN]+fwame[FN]))
    fwame['F1'] = prep(2 * ((fwame['Precision_PPV'] * fwame['Recall'])/(fwame['Precision_PPV'] + fwame['Recall'])))
    return fwame

def compare_dicts(raw_dyct_one, raw_dyct_two):
    one,two = dc(raw_dyct_one),dc(raw_dyct_two)

    for dyct in [one,two]:
        for key in list(dyct.keys()):
            if from_nan(dyct[key]) == None:
                dyct[key] = np.nan

    return set(one.items()) ^ set(two.items())

diff_lists = lambda one,two: set(one) ^ set(two)
same_dicts = lambda dyct_one, dyct_two: compare_dicts(dyct_one, dyct_two) == set()

def contains_dict(list_dicts, current_dict):
    for dyct in list_dicts:
        if same_dicts(dyct, current_dict):
            return True
    return False

def frame_dycts(frame):
    """
    output = []
    for row in frame.itertuples():
        output += [row._asdict()]
    return output
    """
    return frame.to_dict('records')

def pd_to_arr(frame):
    return frame_dycts(frame)

def pd_to_jsonl(frame):
    output = []
    for row in pd_to_arr(frame):
        output += [json.dumps(row)]
    return output

def pd_to_jsonl_file(frame, foil):
    with open(foil,'w+') as writer:
        for line in pd_to_jsonql(frame):
            writer.write(str(line) + "\n")
    return True

def jsons_to_jsonl(jsons):
    if not isinstance(jsons,list):
        return []
    output = []
    for js in jsons:
        output += [json.dumps(js)]
    return output

def dyct_frame(raw_dyct,deepcopy:bool=True):
    dyct = dc(raw_dyct) if deepcopy else raw_dyct
    for key in list(raw_dyct.keys()):
        dyct[key] = [dyct[key]]
    return pd.DataFrame.from_dict(dyct)

def dyct_to_pd(raw_dyct, deepcopy:bool=True):
    return dyct_frame(raw_dyct, deepcopy)

def arr_to_pd(array_of_dictionaries, ignore_index:bool=True):
    try:
        return pd.concat( list(map( dyct_frame,array_of_dictionaries )), ignore_index=True )
    except Exception as e:
        print(f"Error:> {e}")
        return None

def jsonl_file_to_pd(foil):
    content = None
    with open(foil,'r') as reader:
        output = jsonl_to_pd(reader.readlines())
    return output

def jsonl_to_pd(json_lines):
    content = []
    for line in json_lines:
        content += [json.loads(line)]
    return arr_to_pd(content)

def logg(foil,string):
    with open(foil,"a+") as writer:
        writer.write(f"{string}\n")

def cur_time_ms():
    now = timr.now()
    return now.strftime('%Y-%m-%dT%H:%M:%S') + ('.%04d' % (now.microsecond / 10000))

def clean_string(foil, perma:bool=False):
    valid_kar = lambda kar: (ord('0') <= ord(kar) and ord(kar) <= ord('9')) or (ord('A') <= ord(kar) and ord(kar) <= ord('z'))
    if perma:
        return ''.join([i for i in foil if valid_kar(i)])
    else:
        return foil.replace(' ', '\ ').replace('&','\&')

def latex_prep(name,prefix="section"):
    prefix,label_prefix = prefix.lower(),prefix.count("s")
    nice_name = name.lower().replace(' ','_')

    return f"\{prefix}{{{name}}} \label{{{'s'*label_prefix}e:{nice_name}}}"

def input_check(message, checkfor):
    return input(message).strip().lower() == checkfor

sub = lambda name:latex_prep(name,"subsection")
subsub = lambda name:latex_prep(name,"subsubsection")

def timeout(timeout=2 * 60 * 60):
    from threading import Thread
    import functools

    def deco(func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            res = [
                Exception('function [%s] timeout [%s seconds] exceeded!' %
                          (func.__name__, timeout))
            ]

            def newFunc():
                try:
                    res[0] = func(*args, **kwargs)
                except Exception as e:
                    res[0] = e

            t = Thread(target=newFunc)
            t.daemon = True
            try:
                t.start()
                t.join(timeout)
            except Exception as je:
                disp('error starting thread')
                raise je
            ret = res[0]
            if isinstance(ret, BaseException):
                raise ret
            return ret

        return wrapper

    return deco

def plant(plantuml_text, _type='png'):
        base = f'''https://www.plantuml.com/plantuml/{_type}/'''

        plantuml_alphabet = string.digits + string.ascii_uppercase + string.ascii_lowercase + '-_'
        base64_alphabet   = string.ascii_uppercase + string.ascii_lowercase + string.digits + '+/'
        b64_to_plantuml = maketrans(base64_alphabet.encode('utf-8'), plantuml_alphabet.encode('utf-8'))

        """zlib compress the plantuml text and encode it for the plantuml server.
        """
        zlibbed_str = compress(plantuml_text.encode('utf-8'))
        compressed_string = zlibbed_str[2:-4]
        return base+base64.b64encode(compressed_string).translate(b64_to_plantuml).decode('utf-8')

def run(cmd, display:bool=False):
    out = lambda string:logg(".run_logs.txt",string)
    try:
        if display:
            out(cmd)
        output = os.popen(cmd).read()
        if display:
            out(output)
        return output
    except Exception as e:
        if display:
            out(output)
        return e

def from_nan(val):
    if str(val).lower() == "nan":
        return None
    else:
        return str(val)

def is_class(value, klass):
    try:
        klass(value)
        return True
    except:
        return False

def to_int(val, return_val=None, return_self:bool=False):
    if from_nan(val) is None:
        return val if return_self else return_val
    elif isinstance(val, (int,float,complex)) or str(val).isdigit():
        return int(val)
    elif is_class(val, float):
        return int(float(val))
    elif is_class(val, complex):
        return int(complex(val))
    return val if return_self else return_val

def zyp(A,B,output=np.NaN):
    _a_one = not pd.isna(A)
    _a_two = A != -1
    _a_three = (not isinstance(A,str) or bool(A))
    _a_four = (not isinstance(A,bool) or A)

    _b_one = not pd.isna(B)
    _b_two = B != -1
    _b_three = (not isinstance(B,str) or bool(B))
    _b_four = (not isinstance(B,bool) or B)

    if _a_one and _a_two and _a_three and _a_four:
        output = A
    elif _b_one and _b_two and _b_three and _b_four:
        output = B

    return output


def set_mito(mitofile:str="mitoprep.py"):
    with open(mitofile,"w+") as writer:
        writer.write("""#!/usr/bin/python3
import os,sys,json,pwd

prefix = "/home/"
suffix = '/.mito/user.json'

paths = [prefix + str(pwd.getpwuid(os.getuid())[0]) + suffix, prefix + 'runner' + suffix]

for file_path in paths:
    try:
        with open(file_path, 'r') as reader:
            contents = json.load(reader)

        contents['user_email'] = 'test@test.com'
        contents['feedbacks'] = [
            {
                'Where did you hear about Mito?': 'Demo Purposes',
                'What is your main code editor for Python data analysis?': 'Demo Purposes'
            }
        ]
        contents['mitosheet_telemetry'] = False

        with open(file_path, 'w') as writer:
            json.dump(contents, writer)
    except:
        pass
""")
    run(f"{sys.executable} {mitofile} && rm {mitofile}")

def wipe_all(exclude:list, starts_with:bool=False, exclude_hidden:bool=True, custom_matcher=None, base_path:str = os.path.abspath(os.curdir) ):
    for itym in os.listdir(base_path):
        save_foil = False

        if starts_with:
            delete_foil = any([ itym.startswith(prefix) for prefix in exclude ])
        elif custom_matcher:
            delete = custom_matcher(itym)
        else:
            delete_foil = any([ itym == match for match in exclude ])

        if (exclude or not itym.startswith(".")) and delete_foil:
            run(f"yes|rm -r {itym}")

def is_not_empty(myString):
    myString = str(myString)
    return (myString is not None and myString and myString.strip() and myString.strip().lower() not in ['nan','none'])

def is_empty(myString):
    return not is_not_empty(myString)

def retrieve_context(file_name:str, line_number:int, context:int=5, patternmatch=lambda _:False) -> str:
    output = ""

    if not os.path.exists(file_name):
        print(f"{file_name} does not exist.")
        return None

    int_num = to_int(line_number)
    if file_name.strip() != "" and int_num:
        file_name,line_number = str(file_name),int_num
        try:
            with open(file_name, 'r') as reader:
                total_lines = reader.readlines()
                start_range, end_range = max(line_number-context,0), min(line_number+context,len(total_lines))
                len_max_zfill = len(str(end_range))

                for itr,line in enumerate(total_lines):
                    if start_range <= itr <= end_range or patternmatch(line.lower()):
                        if itr == line_number:
                            output = f'{output}{str(itr).zfill(len_max_zfill)} !> {line}'
                        else:
                            output = f'{output}{str(itr).zfill(len_max_zfill)} => {line}'

        except Exception as e:
            print(f"Exception: {e}")
    return output

def print_context(source_code:str, line_numbering=None, code_formatting=lambda line:line, print_out:bool=False):
    contents = []
    if line_numbering is None:
        line_numbering = lambda num: str(num).zfill(len(str(len(source_code.split("\n")))))

    for itr,line in enumerate(source_code.split("\n")):
        current_line = f"{line_numbering(itr)}: {code_formatting(line)}"
        if print_out:
            print(current_line)
        contents += [current_line]

    return "\n".join(contents)

import_global_context = lambda line: "import" in line.lower() or "global" in line.lower()

def get_line_from_context(line_num:int, context:str,_default=""):
    try:
        for line in row.context.split('\n'):
            if int(line.split(' ')[0]) == line_num:
                return line
    except:
        pass
    return _default

def get_lines_from_context(match:str, line_num:int, context:str,_default=""):
    return match in get_line_from_context(line_num, context,_default) or match

class SqliteConnect(object):
    """
    Sample usage:
    ```
    with SqliteConnect("dataset.sqlite") as sql:
        container = pd.read_sql(sql.table_name, sql.connection_string)
    ...
    with SqliteConnect("dataset.sqlite") as sql:
        container.to_sql(sql.table_name, sql.connection, if_exists='replace')
    ```
    """
    def __init__(self,file_name:str,echo:bool=False):
        #https://datacarpentry.org/python-ecology-lesson/09-working-with-sql/index.html
        #https://stackoverflow.com/questions/305378/list-of-tables-db-schema-dump-etc-using-the-python-sqlite3-api
        #https://stackoverflow.com/questions/34570260/how-to-get-table-names-using-sqlite3-through-python
        self.file_name = file_name
        self.table_name = "dataset"
        self.echo = echo
        self.connection_string = f"sqlite:///{self.file_name}"
        self.dataframes = {}

    def __enter__(self):
        existed = os.path.exists(file_name)
        self.engine = create_engine(self.connection_string, echo=self.echo)
        self.connection = self.engine.connect()

        if existed:
            current_cursor = self.connection.cursor()
            current_cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table';")
            for name,_ in current_cursor.fetchall():
                self.dataframes[name] = pd.read_sql_query(f"SELECT * FROM {name}", self.connection) 

            current_cursor = None

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()
        return self

    def add_pandaframe(self, dataframe, sheet_name:str=None):
        while sheet_name in self.dataframes.keys():
            sheet_name = sheet_name + "_"
        self.dataframes[sheet_name] = dataframe
        dataframe.to_sql(sheet_name, self.connection)

    def add_excel(self,fileName):
        dataframes = {}
        try:
            for table_name, frame in pd.read_excel(fileName, engine="openpyxl", sheet_name=None).items():
                dataframes[table_name] = frame
        except Exception as e:
            print(e)
            print(f"Issue parsing the dataframe file: {fileName}")
            pass
        [self.add_pandaframe(frame, key) for key,frame in dataframes.items()]

    def to_excel(self,filename):
        try:
            with xcyl(filename) as writer:
                if self.dataframes == {}:
                    for table_name in self.connection.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall():
                        writer.addr(table_name[0],pd.read_sql_query(f"SELECT * FROM {table_name};",self.connection))
                else:
                    for key,value in self.dataframes.items():
                        writer.addr(key,value)
        except Exception as e:
            print(e)

class ephfile(object):
    def __init__(self,foil=None,contents=None,create=True):
        if foil is None:
            import tempfile
            self.named = tempfile.NamedTemporaryFile()
            self.foil = self.named.name
        else:
            self.named = None
            if not os.path.exists(foil) and create:
                os.system("touch " + str(foil))
            self.foil = foil

        if contents:
            if not isinstance(contents,list):
                contents = [contents]
            for cont in contents:
                contz = str(cont)
                if self.named:
                    self.named.write(str.encode(contz + "\n"))
                else:
                    with open(self.foil,"a+") as writer:
                        writer.write(contz)

    @property
    def contents(self):
        with open(self.foil,'r') as reader:
            return '\n'.join(reader.readlines())

    def __iadd__(self,contents):
        if not isinstance(contents,list):
            contents = [contents]

        contz = '\n'.join([str(x) for x in contents])
        if self.named:
            self.named.write(str.encode(contz + "\n"))
        else:
            with open(self.foil,"a+") as writer:
                writer.write(contz)

        return self
    
    def __call__(self):
        return self.foil

    def __enter__(self):
        return self

    def close(self):
        try:
            if self.named:
                self.named.close()
            else:
                try:
                    os.remove(self.foil)
                except:
                    try:
                        os.system("yes|rm -r " + str(self.foil))
                    except Exception as e:
                        pass
        except Exception as e:
            print(e)
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return self

def cmt_json(input_foil):
    contents = None
    import shutil
    try:
        with ephfile(input_foil.replace('.json','_back.json')) as eph:
            shutil.copyfile(input_foil,eph())
            from fileinput import FileInput as finput
            with finput(eph(),inplace=True,backup=None) as foil:
                for line in foil:
                    if not line.strip().startswith("//"):
                        print(line,end='')
            with open(eph(),'r') as reader:
                contents = json.load(reader)
    except Exception as e:
        print(e)
    return contents

class HuggingFace(object):
    def __init__(self,repo,repo_type="dataset",use_auth=True):
        """
        https://rebrand.ly/hugface

        https://huggingface.co/docs/huggingface_hub/quick-start
        https://huggingface.co/docs/huggingface_hub/how-to-upstream
        https://huggingface.co/docs/huggingface_hub/how-to-downstream
        """
        from huggingface_hub import HfApi

        self.api = HfApi()
        self.repo = repo
        self.repo_type = repo_type
        self.auth=use_auth
        self.downloaded_files = []
        self.opened=False

    def open(self):
        if isinstance(self.auth,str):
            from pathlib import Path
            hugging_face = f"{str(Path.home())}/.huggingface/"
            
            for cmd in [
                f"mkdir -p {hugging_face}",
                f"rm {hugging_face}/token",
                f"touch {hugging_face}/token"
            ]:
                try:
                    print(cmd);os.system(cmd)
                except:
                    pass

            with open(f"{hugging_face}/token","a") as writer:
                writer.write(self.auth)
            self.auth = True
        self.opened = True
        return
    def close(self):
        for foil in self.downloaded_files:
            try:
                os.remove(foil)
            except:
                try:
                    os.system("yes|rm " + str(foil))
                except Exception as e:
                    print("Failed to remove the cached file " +str(foil))
                    print(e)
                    pass
        return
    def download(self, file_path=None,revision=None):
        if not self.opened:
            self.open()
        #https://huggingface.co/docs/huggingface_hub/v0.9.0/en/package_reference/file_download#huggingface_hub.hf_hub_download
        if file_path and isinstance(file_path,str):
            from huggingface_hub import hf_hub_download
            return hf_hub_download(
                repo_id=self.repo,
                filename=file_path,
                revision=revision,
                repo_type=self.repo_type,
                use_auth_token=self.auth
            )
        return None
    def upload(self, path=None,path_in_repo=None):
        if not self.opened:
            self.open()
        if path:
            if isinstance(path,str) and os.path.isfile(path):
                #https://huggingface.co/docs/huggingface_hub/v0.9.0/en/package_reference/hf_api#huggingface_hub.HfApi.upload_file
                self.api.upload_file(
                    path_or_fileobj=path,
                    path_in_repo=path_in_repo or path,
                    repo_id=self.repo,
                    repo_type=self.repo_type,
                )
            elif isinstance(path,str) and os.path.isdir(path):
                #https://huggingface.co/docs/huggingface_hub/v0.9.0/en/package_reference/hf_api#huggingface_hub.HfApi.upload_folder
                self.api.upload_file(
                    folder_path=path,
                    path_in_repo=path_in_repo or path,
                    repo_id=self.repo,
                    repo_type=self.repo_type,
                )
            else:
                print("Entered path " + stsr(path) + " is not supported.")
            return True
        return False
    def files(self,revision=None):
        if not self.opened:
            self.open()
        # https://huggingface.co/docs/huggingface_hub/v0.9.0/en/package_reference/hf_api#huggingface_hub.HfApi.list_repo_files
        return self.api.list_repo_files(
            repo_id=self.repo,
            revision=revision,
            repo_type=self.repo_type
        )
    def delete_file(self,path_in_repo=None,revision=None):
        if not self.opened:
            self.open()
        # https://huggingface.co/docs/huggingface_hub/v0.9.0/en/package_reference/hf_api#huggingface_hub.HfApi.delete_file
        if path_in_repo:
            self.api.delete_file(
                path_in_repo=path_in_repo,
                repo_id=self.repo,
                repo_type=self.repo_type,
                revision=revision
            )
        return False
    def __enter__(self):
        self.open()
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return self
    def __iadd__(self, path):
        self.upload(path)
        return self
    def __getitem__(self,foil):
        return self.download(foil)
    def __setitem__(self,key,value):
        self.upload(value,key)
    def __delitem__(self,item):
        return self.delete_file(item)
    def __str__(self):
        return self.files()
    def __contains__(self, item):
        return item in self.files()
    def __call__(self,item):
        return self.download(item) if item in self else None

class telegramBot(object):
    """
    Sample usage:
    ```
    with telegramBot("botID", "chatID") as bot:
        bot.msg("a")
    ```
    """
    def __init__(self,botID:str,chatID:str):
        self.bot = Bot(botID)
        self.chatID = chatID
        self.msg_lock = Lock()
        self.upload_lock = Lock()
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.bot = None
        return self
    def msg(self,msg:str,print_out:bool=False):
        self.msg_lock.acquire()
        try:
            if msg.strip() == "":
                msg = "EMPTY"
            try:
                self.bot.send_message(self.chatID,msg)
                if print_out:
                    print(msg)
            except Exception as e:
                print(e)
                pass
        finally:
            self.msg_lock.release()
    def msg_out(self, msg:str):
        self.msg(msg,True)
    def upload(self,path:str,caption:str='',confirm:bool=False):
        self.upload_lock.acquire()
        try:
            if os.path.exists(path):
                self.bot.send_document(chat_id = self.chatID,document=open(path,'rb'),caption=caption)
                self.msg(f"File {path} has been uploaded")
                if confirm:
                    self.msg(f"File {path} has been uploaded")
        finally:
            self.upload_lock.release()
    def upload_video(self,path:str,caption:str=''):
        self.upload_lock.acquire()
        try:
            if os.path.exists(path):
                #https://python-telegram-bot.readthedocs.io/en/stable/telegram.bot.html?highlight=send_video#telegram.Bot.send_video
                self.bot.send_video(chat_id = self.chatID,video=open(path,'rb'),caption=caption)
        finally:
            self.upload_lock.release()

@silent_exec()
def save_frames(frame, frame_name, output_type):
    if output_type == 'csv':
        frame.to_csv(clean_string(frame_name) + ".csv")
    if output_type == 'pkl':
        frame.to_pickle(clean_string(frame_name) + ".pkl")

class excelwriter(object):
    def __init__(self,filename):
        if not filename.endswith(".xlsx"):
            filename += ".xlsx"

        self.append = os.path.exists(filename)
        self.filename = filename

        if self.append:
            self.writer = pd.ExcelWriter(filename, engine="xlsxwriter")
        self.dataframes = []
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.append:
            for (frame, frame_name) in self.dataframes:
                for output_type in ["csv","pkl"]:
                    save_frames(frame, frame_name, output_type)

            try:
                self.writer.save()
            except:
                pass
        self.writer = None
        return self

    def __iadd__(self, sheet_name,dataframe):
        self.add_frame(sheet_name,dataframe)

    def add_frame(self,sheet_name,dataframe):
        if len(sheet_name) > 26:
            sheet_name = f"EXTRA_{len(self.dataframes)}"

        self.dataframes += [(dataframe, clean_string(sheet_name))]

        if self.append:
            """
            https://stackoverflow.com/questions/47737220/append-dataframe-to-excel-with-pandas#answer-64824686
            """
            with pd.ExcelWriter(self.filename, mode="a",engine="openpyxl") as f:
                dataframe.to_excel(f, sheet_name=sheet_name)

        else:
            try:
                #https://xlsxwriter.readthedocs.io/example_pandas_table.html
                dataframe.to_excel(self.writer, sheet_name=sheet_name, startrow=1,header=False,index=False)
                worksheet = self.writer.sheets[sheet_name]
                (max_row, max_col) = dataframe.shape
                worksheet.add_table(0, 0, max_row, max_col - 1, {'columns': [{'header': column} for column in dataframe.columns]})
                worksheet.set_column(0, max_col - 1, 12)
            except:
                pass

def append_to_excel(fpath, df, sheet_name):
    """
    https://stackoverflow.com/questions/47737220/append-dataframe-to-excel-with-pandas#answer-64824686
    """
    try:
        with pd.ExcelWriter(fpath, mode="a", engine="openpyxl") as f:
            df.to_excel(f, sheet_name=sheet_name)

        with pd.ExcelWriter(fpath, engine="xlsxwriter") as writer:
            worksheet = writer.sheets[sheet_name]
            (max_row, max_col) = df.shape
            worksheet.add_table(0, 0, max_row, max_col - 1,{'columns': [{'header': column} for column in df.columns]})
            worksheet.set_column(0, max_col - 1, 12)
    except:
        pass

class xcyl(object):
    """
    the new excel object
    """
    def __init__(self,filename:str="TEMP_VALUE", values:dict = {}, useIndex:bool=False):
        if not filename.endswith(".xlsx"):
            filename += ".xlsx"
        self.filename = filename
        self.cur_data_sets = values
        self.useIndex = useIndex
        return None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if os.path.exists(self.filename):
                for key,value in self.cur_data_sets.items():
                    append_to_excel(self.filename,value,key)
            else:
                with pd.ExcelWriter(self.filename, engine="xlsxwriter") as writer:
                    for itr, (key, value) in enumerate(self.cur_data_sets.items()):
                        value.to_excel(writer, sheet_name=key, startrow=1, header=False, index=self.useIndex)
                        worksheet = writer.sheets[key]
                        (max_row, max_col) = value.shape
                        worksheet.add_table(0, 0, max_row, max_col - 1,
                                    {'columns': [{'header': column} for column in value.columns]})
                        worksheet.set_column(0, max_col - 1, 12)
        except Exception as e:
            print(f"Exception :> {e}")
            zyp_name = self.filename + ".zip"
            for key,value in self.cur_data_sets.items():
                value.to_csv(str(key) + ".csv")
                #os.system(f"7z a {zyp_name} {key}.csv -sdel")

        return self

    def addr(self, sheet_name, dataframe):
        while sheet_name in list(self.cur_data_sets.keys()):
            sheet_name += "_"
        self.cur_data_sets[sheet_name] = dataframe
        return self
    def add_frame(self,sheet_name,dataframe):
        self.addr(sheet_name,dataframe)
    def sanity(self):
        return True

def grab_sheet(sheet_name:str='',file_name:str='RawResults.xlsx'):
    import pandas as pd;from openpyxl import load_workbook
    sheet_names = load_workbook(file_name, read_only=True, keep_links=False).sheetnames
    if sheet_name in sheet_names:
        return pd.read_excel(file_name,engine="openpyxl",sheet_name=sheet_name)
    print(f"{sheet_name} not found in {sheet_names}")
    return None

def diff_in_frames(_from, _to):
    df1, df2 = dc(_from), dc(_to)
    for x in [df1, df2]:
        x.replace(np.nan, "Empty", inplace=True)
    df_all = pd.concat([df1, df2], axis='columns', keys=['First', 'Second'])
    df_final = df_all.swaplevel(axis='columns')[df1.columns[1:]]
    def highlight_diff(data, color='yellow'):
        attr = 'background-color: {}'.format(color)
        other = data.xs('First', axis='columns', level=-1)
        return pd.DataFrame(np.where(data.ne(other, level=0), attr, ''),
                            index=data.index, columns=data.columns)

    return df_final.style.apply(highlight_diff, axis=None)

def heatmap(frame, column, min_to_max:bool=False, output_frame_name:str=None):
    cmap = matplotlib.cm.get_cmap('RdYlGn')
    norm = mpl.colors.Normalize(frame[column].min(), frame[column].max())
    def colorRow(col):
        return [f'background-color: {mpl.colors.to_hex(cmap(norm(col[column])))}' for _ in col]
    output_frame = frame.reset_index().style.apply(colorRow,axis=1)
    if output_frame_name:
        if not output_frame_name.endswith('.xlsx'):
            output_frame_name += ".xlsx"
        try:
            output_frame.to_excel(output_frame_name)
        except Exception as e:
            print(f"Issue writing the file out :> {e}")
            pass
    return output_frame

class GRepo(object):
    """
    Sample usage:
    with GRepo("https://github.com/owner/repo","v1","hash") as repo:
        os.path.exists(repo.reponame) #TRUE
    """
    def __init__(self, reponame:str, repo:str, tag:str=None, commit:str=None,delete:bool=True,silent:bool=True,write_statistics:bool=False,local_dir:bool=False,logfile:str=".run_logs.txt",zip_url:str=None, jsonl_file:str=None,
    archive_log:str=None):
        self.delete = delete
        self.print = not silent
        self.out = lambda string:logg(logfile,string)
        self.write_statistics = write_statistics
        self.tag = None
        self.commit = commit or None
        self.reponame = reponame
        self.cloneurl = None
        self.zip_url_base = zip_url
        self.jsonl = jsonl_file
        self.archive_log = archive_log
        if local_dir:
            self.url = "file://" + self.reponame
            self.full_url = repo
        else:
            repo = repo.replace('http://','https://')
            self.url = repo
            self.full_url = repo
            if self.write_statistics:
                try:
                    self.GRepo = Github().get_repo(repo.replace("https://github.com/",""))
                except Exception as e:
                    if self.print:
                        self.out(f"Issue with checking the statistics: {e}")
                    pass

            self.cloneurl = "git clone --depth 1"
            if is_not_empty(tag):
                self.tag = tag
                self.cloneurl += f" --branch {tag}"
                self.full_url += "<b>" + tag

            if is_not_empty(self.commit):
                self.full_url += "<#>" + self.commit

    def __enter__(self):
        if not os.path.exists(self.reponame) and self.url.startswith("https://github.com/"):
            self.out(f"Waiting between scanning projects to ensure GitHub Doesn't get angry")
            wait_for(5, silent=not self.print)
            run(f"{self.cloneurl} {self.url}", display=self.print)

            if is_not_empty(self.commit):
                run(f"cd {self.reponame} && git reset --hard {self.commit} && cd ../", display=self.print)

        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if self.delete:
                if self.print:
                    self.out("Deleting the file")

                run(f"yes|rm -r {self.reponame}", display=self.print)
        except Exception as e:
            if self.print:
                self.out(f"Issue with deleting the file: {e}")

        try:
            if self.write_statistics:
                foil_out = ".github_stats.csv"
                make_header = not os.path.exists(foil_out)

                with open(foil_out,"a+") as writer:
                    if make_header:
                        writer.write("RepoName,RepoURL,RepoTopics,Stars\n")
                    writer.write(','.join( [self.reponame,self.GRepo.url, ':'.join(list(self.GRepo.get_topics())),str(self.GRepo.stargazers_count)] ) + "\n")
        except Exception as e:
            if self.print:
                self.out(f"Issue with writing the statistics: {e}")

        if self.archive_log:
            with open(self.archive_log,"a+") as writer:
                writer.write(f"{self.reponame},{save_link(self.url)}\n")

        return self
    def get_info(self):
        return {
            'URL':self.url,
            'RepoName':self.reponame,
            'Commit':self.commit,
            'FullUrl':self.full_url,
            'CloneUrl':self.cloneurl,
            'datetime':timr.utcnow().strftime('%Y%m%dT%H%M%S')
        }
    def get_info_frame(self):
        return dyct_frame(self.get_info())

    @property
    def zip_url(self):
        if self.zip_url_base is not None:
            return zip_url_base

        if not self.url.startswith("https://github.com/"):
            print("NONE")
            return None

        # url_builder = "https://web.archive.org/save/" + repo.url + "/archive"
        url_builder = self.url + "/archive"
        if is_not_empty(self.commit):
            # https://github.com/owner/reponame/archive/hash.zip
            url_builder += f"/{self.commit}.zip"

        if not is_not_empty(self.commit):
            # https://web.archive.org/save/https://github.com/owner/reponame/archive/refs/heads/tag.zip
            url_builder += f"/refs/heads"
            if not is_not_empty(self.tag):
                for base_branch in ['master', 'main']:
                    temp_url = url_builder + f"/{base_branch}.zip"
                    if live_link(temp_url):
                        url_builder = temp_url
                        break
                    time.sleep(4)
            elif is_not_empty(self.tag):
                url_builder += f"/{self.tag}.zip"

        self.zip_url_base = url_builder
        return self.zip_url_base

    def save_link(self):
        return save_link(self.zip_url)

class GitHubRepo(GRepo):
    def __init__(self, repo:str, tag:str=None, commit:str=None,delete:bool=True,silent:bool=True,write_statistics:bool=False,local_dir:bool=False,logfile:str=".run_logs.txt"):
        reponame = repo.replace("http://", "https://").replace('https://github.com/','').split('/')[-1].replace('.git','')
        super().__init__(reponame, repo, tag, commit, delete, silent, write_statistics, local_dir, logfile)

class ThreadMgr(object):
    def __init__(self,max_num_threads:int=100,time_to_wait:int=10):
        try:
            import thread
        except ImportError:
            import _thread as thread
        self.max_num_threads = max_num_threads
        self.threads = []
        self.time_to_wait = time_to_wait
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        return self
    def __iadd__(self,obj):
        while len([tread for tread in self.threads if tread.isAlive()]) >= self.max_num_threads:
            import time
            time.sleep(self.time_to_wait)

        self.threads += [obj]
        return self

#https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console
def progressBar(iterable, prefix = 'Progress', suffix = 'Complete', decimals = 1, length = 100, fill = '█', printEnd = "\n"):
    """
    Call in a loop to create terminal progress bar
    @params:
    iterable    - Required  : iterable object (Iterable)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    total = len(iterable)
    # Progress Bar Printing Function
    def printProgressBar(iteration):
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + '-' * (length - filledLength)
        print(f'{printEnd}{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Initial Call
    printProgressBar(0)
    # Update Progress Bar
    for i, item in enumerate(iterable):
        yield item
        printProgressBar(i + 1)
    # Print New Line on Complete
    print()

def wait_for(time_num:int,silent:bool=False):
    import time as cur
    ranger = range(time_num)
    if not silent:
        for _ in progressBar(ranger,  prefix='Waiting',suffix="Complete",length=int(time_num)):
            cur.sleep(1)
    else:
        for _ in ranger:
            cur.sleep(1)
    return

def safe_get(obj, attr, default=None):
    if hasattr(obj,attr) and getattr(obj,attr) is not None and getattr(obj,attr).strip().lower() not in ['','none','na']:
        return getattr(obj,attr)
    else:
        return default

def get_system_info():
    return pd.DataFrame(
        [{
            "SystemInfo":f"OS",
            "Value"     :f"{platform.system()}"
        },{
            "SystemInfo":f"VERSION",
            "Value"     :f"{platform.release()}"
        },{
            "SystemInfo":f"CPU",
            "Value"     :f"{platform.machine()}"
        },{
            "SystemInfo":f"RAM",
            "Value"     :str(round(psutil.virtual_memory().total / (1024.0 **3)))+" GB"
        },{
            "SystemInfo":f"RUNNING INSIDE DOCKER",
            "Value"     :f"{os.path.exists('/.dockerenv') or (os.path.isfile('/proc/self/cgroup') and any('docker' in line for line in open('/proc/self/cgroup')))}"
        },{
            "SystemInfo":f"TIME RAN",
            "Value"     :cur_time
        }],columns = ["SystemInfo","Value"]
    )

def isMac():
    return platform.system().lower() == 'darwin'

docker_base = 'docker' if isMac() else 'sudo docker'
def mac_addr():
    """
    Return the mac address of the current computer
    """
    return str(':'.join(re.findall('..', '%012x' % uuid.getnode())))

def of_list(obj: object, functor=None) -> list:
    if not functor or functor is None:
        def functor(x):
            return x

    if isinstance(obj, list):
        return [functor(x) for x in obj]
    else:
        return [functor(obj)]

#https://thispointer.com/python-get-file-size-in-kb-mb-or-gb-human-readable-format/
class SIZE_UNIT(enum.Enum):
    BYTES = 1
    KB = 2
    MB = 3
    GB = 4


def convert_unit(size_in_bytes, unit):
    """ Convert the size from bytes to other units like KB, MB or GB"""
    if unit == SIZE_UNIT.KB:
        return size_in_bytes/1024
    elif unit == SIZE_UNIT.MB:
        return size_in_bytes/(1024*1024)
    elif unit == SIZE_UNIT.GB:
        return size_in_bytes/(1024*1024*1024)
    else:
        return size_in_bytes

def fsize(file_name, size_type = SIZE_UNIT.GB ):
    """ Get file in size in given unit like KB, MB or GB"""
    size = os.path.getsize(file_name)
    return round(convert_unit(size, size_type),2)

def load_env(file_path = ".env.json"):
    with open(file_path,"r") as reader:
        contents = json.load(reader)
    return contents

def intadd(dyct,name):
    result = 0

    if name in dyct:
        result = dyct[name] + 1

    dyct[name] = result
    return result
