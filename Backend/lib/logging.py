'''
#############################################################################################
@brief Program logging functions. Formatting messages
#############################################################################################
'''

from enum import Enum
from datetime import datetime

class WarningLevel(Enum):
    Info = 0
    Warning = 1
    Error = 2

def logging(_type, _msg):
    if _type == WarningLevel.Info:
        preFix = 'INFO>'
    elif _type == WarningLevel.Warning:
        preFix = 'WARNING>'
    elif _type == WarningLevel.Error:
        preFix = 'ERROR>'

    print('{0} {1} {2}'.format(datetime.now().strftime('%H.%M.%S.%f'), preFix, _msg))

def log(_msg):
    logging(WarningLevel.Info, _msg)

def log_warning(_msg):
    logging(WarningLevel.Warning, _msg)

def log_error(_msg):
    logging(WarningLevel.Error, _msg)







