'''
#############################################################################################
@brief Program logging functions. Formatting messages
#############################################################################################
'''

import os

from enum import Enum
from datetime import datetime

class WarningLevel(Enum):
    Info = 0
    Warning = 1
    Error = 2

LogFile = '{}//Logs//backendLog.txt'.format(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
FirstLogging = True

def logging(_type, _msg):
    global FirstLogging

    if _type == WarningLevel.Info:
        preFix = 'INFO>'
    elif _type == WarningLevel.Warning:
        preFix = 'WARNING>'
    elif _type == WarningLevel.Error:
        preFix = 'ERROR>'

    logText = '{0}-{1} {2} {3}'.format(datetime.now().strftime('%d.%m.%Y'), datetime.now().strftime('%H:%M:%S.%f'), preFix, _msg)

    print(logText)

    if FirstLogging:
        if not os.path.exists(os.path.dirname(LogFile)):
            os.mkdir(os.path.dirname(LogFile))
        if os.path.exists(LogFile):
            os.remove(LogFile)
        FirstLogging = False

    # Write in log file
    f = open(LogFile, "a")
    f.write(logText +"\n")
    f.close()

def log(_msg):
    logging(WarningLevel.Info, _msg)

def log_warning(_msg):
    logging(WarningLevel.Warning, _msg)

def log_error(_msg):
    logging(WarningLevel.Error, _msg)







