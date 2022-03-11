from __future__ import print_function
import os, sys, pwd, json, pandas as pd, numpy as np, sqlite3, pwd, uuid, platform, re, base64, string,enum
from datetime import datetime as timr
from sqlite3 import connect
from glob import glob
import functools
import httplib2
import six
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
from telegram import Update, ForceReply, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from github import Github

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

def install_import(importname):
    os.system(f"{sys.executable} -m pip install {importname} --upgrade")

def user():
    return str(pwd.getpwuid(os.getuid())[0]).strip().lower()

percent = lambda x,y: ("{0:.2f}").format(100 * (x / float(y)))
cur_time = str(timr.now().strftime('%Y_%m_%d-%H_%M'))
rnd = lambda _input: f"{round(_input * 100)} %"
similar = lambda x,y:SequenceMatcher(None, a, b).ratio()*100

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

import_global_context = lambda string: "import" in line.lower() or "global" in line.lower()

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
        self.file_name = file_name
        self.table_name = "dataset"
        self.echo = echo
        self.connection_string = f"sqlite:///{self.file_name}"
    def __enter__(self):
        self.engine = create_engine(self.connection_string, echo=self.echo)
        self.connection = self.engine.connect()
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()
        return self
    def add_pandaframe(self, dataframe, sheet_name:str=None):
        dataframe.to_sql(sheet_name, self.connection)
    def add_excel(self,fileName):
        dataframes = {}
        try:
            for table_name, frame in pd.read_excel('somefile.xlsx', sheet_name=None).items():
                dataframes[table_name] = frame
        except:
            print(f"Issue parsing the dataframe file: {fileName}")
            dataframes = {}
            pass
        [self.add_pandaframe(frame, key) for key,frame in dataframes.items()]

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
    def msg(self,msg:str):
        self.msg_lock.acquire()
        try:
            if msg.strip() == "":
                msg = "EMPTY"
            try:
                self.bot.send_message(self.chatID,msg)
            except Exception as e:
                print(e)
                pass
        finally:
            self.msg_lock.release()
    def upload(self,path:str):
        self.upload_lock.acquire()
        try:
            if os.path.exists(path):
                self.bot.send_document(chat_id = self.chatID,document=open(path,'rb'))
                self.msg(f"File {path} has been uploaded")
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

        with pd.ExcelWriter(filename, engine="xlsxwriter") as writer:
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
    def __init__(self,filename:str="TEMP_VALUE", values:dict = {}):
        if not filename.endswith(".xlsx"):
            filename += ".xlsx"
        self.filename = filename
        self.cur_data_sets = {}
        return None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        zyp_name = self.filename + ".zip"
        for key,value in self.cur_data_sets.items():
            value.to_csv(str(key) + ".csv")
            os.system(f"7z a {zyp_name} {key}.csv -sdel")

        with pd.ExcelWriter(self.filename, engine="xlsxwriter") as writer:
            for itr, (key, value) in enumerate(self.cur_data_sets.items()):
                print(value)
                value.to_excel(writer, sheet_name=key, startrow=1, header=False, index=False)
                worksheet = writer.sheets[key]
                (max_row, max_col) = value.shape
                worksheet.add_table(0, 0, max_row, max_col - 1,
                                    {'columns': [{'header': column} for column in value.columns]})
                worksheet.set_column(0, max_col - 1, 12)
        return self

    def addr(self, sheet_name, dataframe):
        while sheet_name in list(self.cur_data_sets.keys()):
            sheet_name += "_"
        self.cur_data_sets[sheet_name] = dataframe
        return self

class GRepo(object):
    """
    Sample usage:
    with GRepo("https://github.com/owner/repo","v1","hash") as repo:
        os.path.exists(repo.reponame) #TRUE
    """
    def __init__(self, reponame:str, repo:str, tag:str=None, commit:str=None,delete:bool=True,silent:bool=True,write_statistics:bool=False,local_dir:bool=False,logfile:str=".run_logs.txt"):
        self.delete = delete
        self.print = not silent
        self.out = lambda string:logg(logfile,string)
        self.write_statistics = write_statistics
        if local_dir:
            self.reponame = reponame
            self.url = "file://" + self.reponame
        else:
            repo = repo.replace('http://','https://')
            self.url = repo
            self.reponame = reponame
            self.commit = commit or None
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

        return self

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
