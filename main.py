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
import os

from datetime import datetime, timedelta
from lib.progEnums import *


class ExecutionController:

    ExecutionTime_Start = None
    ExecutionTime_Stop = None
    Browser = None

    CourseLayout = None
    WeatherForecast = None

    def __init__(self):
        pass

    def main(self):

        indleTimeInSec = 1
        initialisationDone = False

        print('Entry - LOOP')

        # Endless loop
        while True:
            # Check if setting file exists
            if os.path.exists(lib.settings.FilePath) and lib.settings.Document is None:
                lib.settings.read()
            else:
                # File was removed
                if not os.path.exists(lib.settings.FilePath):
                    lib.settings.Document = None
                # File has changed
                if lib.settings.sizeHasChanged():
                    lib.settings.read()

            # New execution in progress
            if lib.settings.Document is not None:
                # Do initialisation 5 minutes before official execution
                if lib.settings.Document['executiontime_converted'] < datetime.now() + timedelta(minutes=5) and not initialisationDone:
                    print('Doing initialisation at', datetime.now())
                    # Clear previous run
                    self.CourseLayout = None
                    self.WeatherForecast = None
                    # Get course layout when 9 course is booked
                    if lib.settings.Document['courseBooking_enum'] == BookingMode.Nine:
                        self.run_course_layout()
                    else:
                        print('Skip course layout because booking 18 course is enabled')
                    # Get weather data if needed
                    if lib.settings.Document['use_nice_weather_golfer']:
                        self.run_weather_forecast()
                    else:
                        print('Skip weather forecast because function disabled')
                    print('Initialisation done')
                    initialisationDone = True

                # Check if execution time is reached
                if lib.settings.Document['executiontime_converted'] < datetime.now():
                    print('New execution time reached at', datetime.now())

                    #TODO: Booking

                    print('Execution done')
                    # Execution done
                    initialisationDone = False
                    lib.settings.Document = None
                else:
                    time.sleep(indleTimeInSec)
            else:
                time.sleep(indleTimeInSec)

    def run_course_layout(self):
        # Start browser
        self.CourseLayout = self.start_browser_course_layout()
        self.Browser.dispose()
        print('Layout list updated')

    def run_weather_forecast(self):
        # Start browser
        self.WeatherForecast = self.start_browser_weather_forecast()
        self.Browser.dispose()
        print('Weather forecast list updated')

    def run_course_booking(self):

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

    # region Start browser
    def start_browser_course_layout(self):
        print('Start browser COURSE LAYOUT update...')
        self.Browser = lib.CBrowser(lib.BrowserType.Chrome, lib.settings)
        return self.Browser.start_browser_course_layout()

    def start_browser_weather_forecast(self):
        print('Start browser WEATHER FORECAST update...')
        self.Browser = lib.CBrowser(lib.BrowserType.Chrome, lib.settings)
        return self.Browser.start_browser_wheater_forecast()


    def start_browser_course_booking(self):
        print('Start browser COURSE BOOKING...')
        self.Browser = lib.CBrowser(lib.BrowserType.Chrome, lib.settings)
        self.Browser.start_browser_course_booking()
    #endregion

if __name__ == "__main__":
    Instance = ExecutionController()
    Instance.main()
