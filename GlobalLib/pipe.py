'''
#############################################################################################
@brief Pipe object to communicate between frontend and backend
@param self.Pipe - Python PIPE
@param self.DebugMode - Print out data recive & data send
#############################################################################################
'''

from enum import Enum
from datetime import datetime

class PipeOperation(Enum):
    Req_CourseLayout = 0
    Resp_CourseLayout = 1
    Req_CourseStatus = 2
    Resp_CourseStatus = 3
    Req_NewReq = 4
    Resp_NewReq = 5
    Req_CancelReq = 6
    Resp_CancelReq = 7
    Req_ReqInProgress = 8
    Resp_ReqInProgress = 9

    BackendBooted = 100

    InvalidOperation = 99


class CPipe:

    Pipe = None
    DebugMode = False

    def __init__(self, conn, debugMode):
        self.Pipe = conn
        self.DebugMode = debugMode

    def get_data(self, timeout=None):
        data = None
        if timeout is None:
            data = self.Pipe.recv()
        else:
            if self.Pipe.poll(timeout):
                data = self.Pipe.recv()

        if data is None:
            return PipeOperation.InvalidOperation, dict()
        elif len(data) != 2:
            raise Exception('Data length corrupt')

        operation = PipeOperation(data[0])
        recvData = data[1]

        if self.DebugMode:
            print('Data recived: {0} - {1}'.format(operation, recvData))

        return operation, recvData

    def send_data(self, operation, data=dict()):
        if self.DebugMode:
            print('Send data: {0} - {1}'.format(operation, data))
        self.Pipe.send([operation, data])

    def new_data_available(self, timeout=None):
        if timeout is None:
            if self.Pipe.poll():
                return True
            else:
                return False
        else:
            if self.Pipe.poll(timeout):
                return True
            else:
                return False

    def dump_recive_buffer(self):
        if self.Pipe.poll():
            data = self.Pipe.recv()
