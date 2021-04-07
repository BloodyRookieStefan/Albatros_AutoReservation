class CStatus:

    Success = False
    Message = ''

    def __init__(self, success, message=''):

        if not success and message == '':
            raise ValueError('No error message set')

        self.Success = success
        self.Message = message

