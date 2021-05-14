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
    InitialisationDone = False

    Timeslots = None
    CourseLayout = None
    WeatherForecast = None

    def __init__(self):
        pass

    def main(self):

        indleTimeInSec = 1
        self.InitialisationDone = False

        print('Entry - MAIN loop')

        # Endless loop
        while True:
            # Check if setting file exists
            if os.path.exists(lib.settings.FilePath) and lib.settings.Document is None:
                lib.settings.read()
                print('New execution order found. Will be executed at', lib.settings.Document['executiontime_converted'])
            else:
                # File was removed
                if not os.path.exists(lib.settings.FilePath) and lib.settings.Document is not None:
                    lib.settings.Document = None
                    print('Existing execution order canceled')
                # File has changed
                if lib.settings.sizeHasChanged():
                    lib.settings.read()
                    print('Existing execution order changed. Will be executed at', lib.settings.Document['executiontime_converted'])

            # New execution in progress
            if lib.settings.Document is not None:
                # Do initialisation 10 minutes before official execution
                if lib.settings.Document['executiontime_converted'] < datetime.now() + timedelta(minutes=10) and not self.InitialisationDone:
                    print('')
                    print('Doing initialisation at', datetime.now())
                    print('')
                    # Clear previous run
                    self.CourseLayout = None
                    self.WeatherForecast = None
                    # Get course layout when 9 course is booked
                    #if lib.settings.Document['courseBooking_enum'] == BookingMode.Nine:
                    #    self.run_course_layout()
                    #else:
                    #    print('Skip course layout because booking 18 course is enabled')
                    # Get weather data if needed
                    if lib.settings.Document['use_nice_weather_golfer']:
                        conditionMet = self.run_weather_forecast()
                        if not conditionMet:
                            print('Weather condition not met. Skip booking')
                            self.endBookingSession()
                        print('Weather condition met')
                    else:
                        print('Skip weather forecast because function disabled')
                    print('Initialisation done')
                    self.InitialisationDone = True

                # Check if execution time is reached
                if lib.settings.Document is not None and lib.settings.Document['executiontime_converted'] < datetime.now():
                    print('')
                    print('New execution time reached at', datetime.now())
                    print('')

                    self.run_course_booking()
                    self.endBookingSession()
                else:
                    time.sleep(indleTimeInSec)
            else:
                time.sleep(indleTimeInSec)

    def run_course_layout(self):
        # Start browser
        self.CourseLayout = None
        self.CourseLayout = self.start_browser_course_layout()
        self.Browser.dispose()
        print('Layout list updated')

    def run_weather_forecast(self):
        # Start browser
        self.WeatherForecast = None
        self.WeatherForecast = self.start_browser_weather_forecast()
        self.Browser.dispose()
        # Check if weather meets requirements

        # Get weather in timslot range
        dayForeCast = None
        for date in self.WeatherForecast:
            day = self.WeatherForecast[date]
            if day.Date is not None and day.Date == lib.settings.Document['date_converted']:
                dayForeCast = day
                break

        if dayForeCast is None:
            return False

        temp = []
        chanceOfRain = []
        maxWind = []

        for time in dayForeCast.Temp:
            if time >= lib.settings.Document['round'][0]['timeslot_timespan_start'].hour and time <= lib.settings.Document['round'][0]['timeslot_timespan_end'].hour:
                temp.append(float(dayForeCast.Temp[time]))
                chanceOfRain.append(float(dayForeCast.ChanceOfRain[time]))
                maxWind.append(float(dayForeCast.Wind[time].replace(',', '.')))

        av_temp = sum(temp) / len(temp)
        av_chanceOfRain = sum(chanceOfRain) / len(chanceOfRain)
        av_maxWind = sum(maxWind) / len(maxWind)

        if av_temp < lib.settings.Document['minTemp_deg'] or av_chanceOfRain > lib.settings.Document['maxRainChange_perc'] or av_maxWind > lib.settings.Document['maxWind_km/h']:
            return False
        else:
            return True

    def run_course_booking(self):

        # Get execution time start
        self.ExecutionTime_Start = time.time()

        # Start browser
        self.Timeslots = None
        self.Timeslots = self.start_browser_course_booking()

        # Check if we find free time slot on course
        selectedTimeslot = None
        for key in self.Timeslots:
            # At first timeslot needs to be free
            if self.Timeslots[key].IsFree:
                # Check if time is in range
                if self.Timeslots[key].Slot >= lib.settings.Document['round'][0]['timeslot_timespan_start'] and \
                        self.Timeslots[key].Slot <= lib.settings.Document['round'][0]['timeslot_timespan_end']:
                    selectedTimeslot = self.Timeslots[key]
                    break

        if selectedTimeslot is None:
            print('FAILED: Could not find valid time slot')
            self.Browser.logout()
            self.Browser.dispose()
            return

        print('Round selected => Timeslot: {0}, Course: {1}, IsFree: {2} '.format(selectedTimeslot.Slot.strftime('%d.%m.%Y - %H:%M'), lib.settings.Document['courseBooking_enum'].name, selectedTimeslot.IsFree))

        self.Browser.reservation(_timeslot=selectedTimeslot)
        self.Browser.partner_reservation(_id=0)
        self.Browser.send_reservation()

        # Get execution time start
        self.ExecutionTime_Stop = time.time()
        print('Execution time:', self.ExecutionTime_Stop - self.ExecutionTime_Start)

        print('Done... Browser program')
        self.Browser.logout()
        self.Browser.dispose()

    def close_browser(self):
        print('Close current browser...')
        self.Browser.dispose()

    def endBookingSession(self):
        print('Remove setting file')
        if os.path.exists(lib.settings.FilePath):
            os.remove(lib.settings.FilePath)

        print('Execution done')
        # Execution done
        self.InitialisationDone = False
        lib.settings.Document = None

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
        return self.Browser.start_browser_course_booking()
    #endregion

if __name__ == "__main__":
    Instance = ExecutionController()
    Instance.main()
