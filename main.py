'''
#############################################################################################
@brief Main file
@param self.ExecutionTime_Start - datetime when execution is started
@param self.Browser - Browser object
@param self.Timeslots_blue - Parsed timeslots course blue
@param self.Timeslots_red - Parsed timeslots course red
@param self.Timeslots_yellow - Parsed timeslots course yellow
#############################################################################################
'''

import lib
import time
import random
import itertools

from datetime import datetime
from lib.progEnums import CourseType


class ExecutionController:

    ExecutionTime_Start = None
    ExecutionTime_Stop = None
    Browser = None

    def __init__(self):
        pass

    def main(self):
        self.run_course_layout()
        while True:
            # TODO: Run course layout ONCE a day
            # TODO: Booking when setting file changed
            pass

    def run_course_layout(self):
        # Start browser
        self.start_browser_course_layout()
        self.Browser.dispose()

    def run_course_booking(self):

        # Wait until execution time is reached
        self.wait_until_time_is_reached()

        # Get execution time start
        self.ExecutionTime_Start = time.time()

        # Start browser
        self.start_browser_course_booking()

        print('')
        print('Init done...')
        print('')
        '''
        round1 = self.get_course_timeslot(_course=combi[0], _timeSlotStart=lib.settings.Document['round'][0]['timeslot_timespan_start'], _timeSlotEnd=lib.settings.Document['round'][0]['timeslot_timespan_end'])

        if round1 is None:
            print('FAILED: Could not find valid time slot')
            return

        print('Round selected => Timeslot: {0}, Course: {1}, IsFree: {2} '.format(round1.Slot.strftime('%d.%m.%Y - %H:%M'), round1.Course.name, round1.IsFree))

        self.Browser.reservation(_timeslot=round1)
        self.Browser.partner_reservation(_id=0)
        self.Browser.send_reservation()

        # Get execution time start
        self.ExecutionTime_Stop = time.time()
        print('Execution time:', self.ExecutionTime_Stop - self.ExecutionTime_Start)

        print('Done... Browser program')
        self.Browser.logout()
        self.Browser.dispose()
        '''

    def wait_until_time_is_reached(self):
        print('Wait for execution date and time...')
        while lib.settings.Document['executiontime_converted'] > datetime.now():
            # Wait some time
            time.sleep(1)
        print('Time reached at', datetime.now())

    def start_browser_course_layout(self):
        print('Start browser COURSE LAYOUT update...')
        self.Browser = lib.CBrowser(lib.BrowserType.Chrome, lib.settings)
        self.Browser.start_browser_course_layout()
        print('Layout list updated')

    def start_browser_course_booking(self):
        print('Start browser COURSE BOOKING...')
        self.Browser = lib.CBrowser(lib.BrowserType.Chrome, lib.settings)
        self.Browser.start_browser_course_booking()

    def close_browser(self):
        print('Close current browser...')
        self.Browser.dispose()

    def get_course_timeslot(self, _course, _timeSlotStart, _timeSlotEnd):

        self.Browser.set_course(_course=_course.name)

        # Parse timetable if not done yet
        timslots = dict()
        if _course == CourseType.Blue:
            if len(self.Timeslots_blue) == 0:
                self.Timeslots_blue = self.Browser.parse_timeslots(CourseType.Blue)
            timeslots = self.Timeslots_blue
        elif _course == CourseType.Red:
            if len(self.Timeslots_red) == 0:
                self.Timeslots_red = self.Browser.parse_timeslots(CourseType.Red)
            timeslots = self.Timeslots_red
        elif _course == CourseType.Yellow:
            if len(self.Timeslots_yellow) == 0:
                self.Timeslots_yellow = self.Browser.parse_timeslots(CourseType.Yellow)
            timeslots = self.Timeslots_yellow

        # Check if we find free time slot on course
        for key in timeslots:
            # At first timeslot needs to be free
            if timeslots[key].IsFree:
                # Check if time is in range
                if timeslots[key].Slot >= _timeSlotStart and timeslots[key].Slot <= _timeSlotEnd:
                    return timeslots[key]

        return None


if __name__ == "__main__":
    Instance = ExecutionController()
    Instance.main()
