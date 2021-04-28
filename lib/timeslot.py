import datetime

class timeslot:

    Str_text = None
    Str_class = None
    Str_href = None
    Str_id = None
    Course = None
    Slot = None
    LinkElement = None
    IsFree = False

    def __init__(self, _class, _timeVal, _linkElement, _course):
        # Click element in order to generate auto id for "used" timeslots
        _linkElement.click()

        self.LinkElement = _linkElement

        self.Str_href = _linkElement.get_attribute('href')
        self.Str_id = _linkElement.get_attribute('id')
        self.Str_text = _timeVal[0]
        self.Str_class = _class

        self.Course = _course

        # Convert timeslot
        timeSplit = _timeVal[0].split(':')
        self.Slot = datetime.datetime(_timeVal[1].year, _timeVal[1].month, _timeVal[1].day, int(timeSplit[0]), int(timeSplit[1]), 0)

        # When there is no ID slot is free
        if self.Str_id is '':
            self.IsFree = True
        else:
            self.IsFree = False
