'''
#############################################################################################
@brief Main file
@param self.ExecutionTime_Start - datetime when execution is started
@param self.ExecutionTime_Stop - datetime when execution is stopped
@param self.Browser - Browser object
@param self.InitialisationDone - Initialisation done for this execution
@param self.Timeslots - Parsed timeslots
@param self.WeatherForecast - Parsed weather forecase
@param self.LastLayoutCheck - datetime of last course layout check
#############################################################################################
'''

import lib
import time
import os

from datetime import datetime, timedelta

class ExecutionController:

    ExecutionTime_Start = None
    ExecutionTime_Stop = None
    Browser = None
    InitialisationDone = False

    Timeslots = None
    WeatherForecast = None

    LastLayoutCheck = None

    def __init__(self):
        pass

    def main(self):

        indleTimeInSec = 1
        self.InitialisationDone = False

        lib.log('Entry - MAIN loop')

        # Endless loop
        while True:
            # ----------------------------------------------
            # Check if setting file exists
            # ----------------------------------------------
            if os.path.exists(lib.settings.FilePath) and lib.settings.Document is None:
                lib.settings.read()
                self.init_new_request()
                print('')
                lib.log('New execution order found. Will be executed at {}'.format(lib.settings.Document['executiontime_converted']))
            else:
                # File was removed
                if not os.path.exists(lib.settings.FilePath) and lib.settings.Document is not None:
                    lib.settings.Document = None
                    lib.log('Existing execution order canceled')
                # File has changed
                if lib.settings.sizeHasChanged():
                    lib.settings.read()
                    self.init_new_request()
                    print('')
                    lib.log('Existing execution order changed. Will be executed at {}'.format(lib.settings.Document['executiontime_converted']))
            # ----------------------------------------------
            # Check if it is time to parse course layout
            # Check layout on startup or at 3 O'Clock in the morning
            # ----------------------------------------------
            if self.LastLayoutCheck is None or (self.LastLayoutCheck.day < datetime.now().day and datetime.now().hour == 3):
                self.run_course_layout()
                self.LastLayoutCheck = datetime.now()
                lib.log('Layout list updated at {}'.format(self.LastLayoutCheck))
            # ----------------------------------------------
            # New execution in progress when we found a settings file
            # ----------------------------------------------
            if lib.settings.Document is not None:
                # Do initialisation 10 minutes before official execution
                if lib.settings.Document['executiontime_converted'] < datetime.now() + timedelta(minutes=10) and not self.InitialisationDone:
                    lib.log('Doing initialisation at {}'.format(datetime.now()))
                    if lib.settings.Document['use_nice_weather_golfer']:
                        conditionMet = self.run_weather_forecast()
                        if not conditionMet:
                            lib.log_warning('Weather condition not met. Skip booking')
                            self.endBookingSession()
                        else:
                            lib.log('Weather condition met')
                    else:
                        lib.log('Skip weather forecast because function disabled')
                    lib.log('Initialisation done')
                    self.InitialisationDone = True

                # Check if execution time is reached => Start 30 seconds early
                if lib.settings.Document is not None and lib.settings.Document['executiontime_converted'] < datetime.now() + timedelta(senconds=30):
                    lib.log('New execution time reached at {}'.format(datetime.now()))

                    #self.run_course_booking()          # ----------------------------------- DISABLED
                    self.endBookingSession()
                else:
                    time.sleep(indleTimeInSec)
            else:
                time.sleep(indleTimeInSec)
            # ----------------------------------------------

    def init_new_request(self):
        # Clear previous run
        self.BrowserType = None
        self.Timeslots = None
        self.WeatherForecast = None

        if lib.settings.Document['browser'].lower() == 'chrome':
            self.BrowserType = lib.BrowserType.Chrome

    def run_course_layout(self):
        # Start browser
        self.start_browser_course_layout()
        self.Browser.dispose()

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
            lib.log('FAILED: Could not find valid time slot')
            self.Browser.logout()
            self.Browser.dispose()
            return

        lib.log('Round selected => Timeslot: {0}, Course: {1}, IsFree: {2} '.format(selectedTimeslot.Slot.strftime('%d.%m.%Y - %H:%M'), lib.settings.Document['courseBooking_enum'].name, selectedTimeslot.IsFree))

        self.Browser.reservation(_timeslot=selectedTimeslot)
        result = self.Browser.partner_reservation(_id=0)
        if result:
            self.Browser.send_reservation()
        else:
            lib.log_warning('Not all partners could be found. Skip reservation')

        # Get execution time start
        self.ExecutionTime_Stop = time.time()
        lib.log('Execution time: {}'.format(self.ExecutionTime_Stop - self.ExecutionTime_Start))

        lib.log('Done... Browser program')
        self.Browser.logout()
        self.Browser.dispose()

    def close_browser(self):
        lib.log('Close current browser...')
        self.Browser.dispose()

    def endBookingSession(self):
        lib.log('Remove setting file')
        while os.path.exists(lib.settings.FilePath):
            try:
                os.remove(lib.settings.FilePath)
            except:
                pass

        lib.log('Execution done')
        # Execution done
        self.InitialisationDone = False
        lib.settings.Document = None

    # region Start browser
    def start_browser_course_layout(self):
        lib.log('Start browser COURSE LAYOUT update...')
        self.Browser = lib.CBrowser(lib.BrowserType.Chrome, lib.settings)
        return self.Browser.start_browser_course_layout()

    def start_browser_weather_forecast(self):
        lib.log('Start browser WEATHER FORECAST update...')
        self.Browser = lib.CBrowser(lib.BrowserType.Chrome, lib.settings)
        return self.Browser.start_browser_wheater_forecast()

    def start_browser_course_booking(self):
        lib.log('Start browser COURSE BOOKING...')
        self.Browser = lib.CBrowser(lib.BrowserType.Chrome, lib.settings)
        return self.Browser.start_browser_course_booking()
    #endregion

if __name__ == "__main__":
    Instance = ExecutionController()
    Instance.main()
