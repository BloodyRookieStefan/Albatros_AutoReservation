'''
#############################################################################################
@brief Parsed timeslot object
@param self.Str_text - times as text (Button text)
@param self.Course - Course ENUM
@param self.Slot - Timeslot in datetime format
@param self.IsFree - Timeslot is free true/false
#############################################################################################
'''

import datetime

class timeslot:

    Str_text = None
    Course = None
    Slot = None
    IsFree = False

    def __init__(self, _timeVal, _course, _isFree):

        self.Str_text = _timeVal[0]
        self.Course = _course
        self.IsFree = _isFree

        # Convert timeslot
        timeSplit = _timeVal[0].split(':')
        self.Slot = datetime.datetime(_timeVal[1].year, _timeVal[1].month, _timeVal[1].day, int(timeSplit[0]), int(timeSplit[1]), 0)