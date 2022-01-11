import os, sys, json, pandas as pd, sqlite3, pwd, uuid, platform, re
from datetime import datetime as timr
from sqlite3 import connect
from glob import glob

def install_import(importname):
    os.system(f"{sys.executable} -m pip install {importname} --upgrade")

try:
    from sqlalchemy import create_engine
    import pandas as pd
    import psutil
    from telegram import Update, ForceReply, Bot
    from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
except:
    install_import("sqlalchemy pandas xlsxwriter psutil python-telegram-bot")
    from sqlalchemy import create_engine
    import pandas as pd
    import psutil
    from telegram import Update, ForceReply, Bot
    from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

percent = lambda x,y: ("{0:.2f}").format(100 * (x / float(y)))
cur_time = str(timr.now().strftime('%Y_%m_%d-%H_%M'))
rnd = lambda _input: f"{round(_input * 100)} %"

def clean_string(foil, perma:bool=False):
    valid_kar = lambda kar: (ord('0') <= ord(kar) and ord(kar) <= ord('9')) or (ord('A') <= ord(kar) and ord(kar) <= ord('z'))
    if perma:
        return ''.join([i for i in foil if valid_kar(i)])
    else:
        return foil.replace(' ', '\ ').replace('&','\&')

def run(cmd):
    try:
        return os.popen(cmd).read()
    except Exception as e:
        return e

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
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.bot = None
        return self
    def msg(self,msg:str):
        if msg.strip() == "":
            msg = "EMPTY"
        try:
            tele_bot.send_message(self.chatID,msg)
        except Exception as e:
            print(e)
            pass
    def upload(self,path:str):
        self.msg(f"Attempting to send file: {path}")
        if os.path.exists(path):
            tele_bot.send_document(chat_id = self.chatID,document=open(path,'rb'))
            self.msg(f"File {path} has been uploaded")
        else:
            self.msg(f"File {path} does not exist")

class excelwriter(object):
    def __init__(self,filename):
        if not filename.endswith(".xlsx"):
            filename += ".xlsx"
        self.writer = pd.ExcelWriter(filename, engine="xlsxwriter")
        self.dataframes = []
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.writer.save()
        except:
            for (frame, frame_name) in self.dataframes:
                frame.to_csv(frame_name + ".csv")
        self.writer = None
        return self

    @staticmethod
    def __table_from_df(writer, sheet_name, dataframe):
        #https://xlsxwriter.readthedocs.io/example_pandas_table.html
        dataframe.to_excel(writer, sheet_name=sheet_name, startrow=1,header=False,index=False)
        worksheet = writer.sheets[sheet_name]
        (max_row, max_col) = dataframe.shape
        worksheet.add_table(0, 0, max_row, max_col - 1, {'columns': [{'header': column} for column in dataframe.columns]})
        worksheet.set_column(0, max_col - 1, 12)

    def add_frame(self,sheet_name,dataframe):
        self.__table_from_df(self.writer, sheet_name, dataframe)
        self.dataframes += [(dataframe, sheet_name)]

#https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console
def progressBar(iterable, prefix = 'Progress', suffix = 'Complete', decimals = 1, length = 100, fill = '█', printEnd = "\n"):
    """
    Call in a loop to create terminal progress bar
    @params:
    iterable	- Required  : iterable object (Iterable)
        prefix	  - Optional  : prefix string (Str)
        suffix	  - Optional  : suffix string (Str)
        decimals	- Optional  : positive number of decimals in percent complete (Int)
        length	  - Optional  : character length of bar (Int)
        fill		- Optional  : bar fill character (Str)
        printEnd	- Optional  : end character (e.g. "\r", "\r\n") (Str)
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

def wait_for(time_num:int):
    import time as cur
    ranger = range(time_num)
    for _ in progressBar(ranger,  prefix='Waiting',suffix="Complete",length=int(time_num)):
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
            "Value"	 :f"{platform.system()}"
        },{
            "SystemInfo":f"VERSION",
            "Value"	 :f"{platform.release()}"
        },{
            "SystemInfo":f"CPU",
            "Value"	 :f"{platform.machine()}"
        },{
            "SystemInfo":f"RAM",
            "Value"	 :str(round(psutil.virtual_memory().total / (1024.0 **3)))+" GB"
        },{
            "SystemInfo":f"RUNNING INSIDE DOCKER",
            "Value"	 :f"{os.path.exists('/.dockerenv') or (os.path.isfile('/proc/self/cgroup') and any('docker' in line for line in open('/proc/self/cgroup')))}"
        },{
            "SystemInfo":f"TIME RAN",
            "Value"	 :cur_time
        }],columns = ["SystemInfo","Value"]
    )

def isMac():
    return platform.system().lower() == 'darwin'

docker_base = 'docker' if isMac() else 'sudo docker'
def mac_addr():
    return str(':'.join(re.findall('..', '%012x' % uuid.getnode())))