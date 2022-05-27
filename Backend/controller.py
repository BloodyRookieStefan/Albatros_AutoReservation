'''
#############################################################################################
@brief Main file for backend
@param self.Pipe - Communication pipe
@param self.Booted - Backend fully initialized
@param self.ExecutionTime_Start - datetime when execution is started
@param self.ExecutionTime_Stop - datetime when execution is stopped
@param self.Browser - Browser object
@param self.InitialisationDone - Initialisation done for this execution
@param self.Timeslots - Parsed timeslots
@param self.WeatherForecast - Parsed weather forecase
@param self.LastLayoutCheck - datetime of last course layout check
@param self.CourseStatus - Dict of last Course Status
@param self.CourseLayout - Dict of last Course Layout
#############################################################################################
'''

import Backend.lib
import time
import os

from datetime import datetime, timedelta
from GlobalLib.pipe import CPipe, PipeOperation

class ExecutionController:
    # Com pipe
    Pipe = None
    # General vars
    Booted = False
    ExecutionTime_Start = None
    ExecutionTime_Stop = None
    Browser = None
    # Parsed timeslots and weather forecast
    Timeslots = None
    WeatherForecast = None
    # Course status and layout
    LastLayoutCheck = None
    CourseStatus = dict()
    CourseLayout = dict()

    def __init__(self):
        pass

    def main(self, conn):
        print('Startup Backend - Params: developmode={0}, fastbootmode={1}, debugmessages={2} ...'.format(Backend.lib.settings.TemplateDocument['developermode'], Backend.lib.settings.TemplateDocument['fastbootmode'], Backend.lib.settings.TemplateDocument['debugmessages']))
        self.Pipe = CPipe(conn, Backend.lib.settings.TemplateDocument['debugmessages'])
        indleTimeInSec = 0.1

        Backend.lib.log('Entry - MAIN loop')

        # Endless loop
        while True:
            # Handle income messages
            self.pipe_handler()

            # ----------------------------------------------
            # Check if it is time to parse course layout
            # Check layout on startup or at 3 O'Clock in the morning
            # ----------------------------------------------
            if self.LastLayoutCheck is None or (self.LastLayoutCheck.day < datetime.now().day and datetime.now().hour == 3):
                if Backend.lib.settings.TemplateDocument['fastbootmode'] == 1 and Backend.lib.settings.TemplateDocument['developermode'] == 1 and self.LastLayoutCheck is None:
                    # Do nothing in this case
                    pass
                else:
                    # Do layout check
                    self.run_course_status_layout()
                # Save current timestamp
                self.LastLayoutCheck = datetime.now()
                Backend.lib.log('Course Layout & Course Status list updated at {}'.format(self.LastLayoutCheck))
            # ----------------------------------------------
            # New execution in progress when we found a settings file
            # ----------------------------------------------
            if Backend.lib.settings.Document is not None:
                # Check if execution time is reached => Start 60 seconds early
                if Backend.lib.settings.Document['executiontime_converted'] < datetime.now() + timedelta(seconds=60):
                    Backend.lib.log('New execution time reached at {}'.format(datetime.now()))

                    self.run_course_booking()
                    self.endBookingSession()
                else:
                    time.sleep(indleTimeInSec)
            else:
                time.sleep(indleTimeInSec)
            # ----------------------------------------------

    def run_course_status_layout(self):
        i = 0
        maxTries = 3
        success = False
        while i < maxTries and not success:
            #try:
                self.CourseStatus = None
                self.CourseLayout = None

                # Start browser
                self.Browser = Backend.lib.CBrowser(Backend.lib.BrowserType.Chrome, Backend.lib.settings)
                Backend.lib.log('Start browser COURSE STATUS update...')
                self.CourseStatus = self.Browser.start_browser_course_status()
                Backend.lib.log('Start browser COURSE LAYOUT update...')
                self.CourseLayout = self.Browser.start_browser_course_layout()

                success = True
            #except Exception as e:
            #    i = i + 1
            #    Backend.lib.log_error(f'Could not run course layout: {str(e)}. Retry {i} of {maxTries}')
            #    self.CourseStatus = dict()
            #    self.CourseLayout = dict()
            #    time.sleep(5)

            #self.Browser.dispose()

    def run_course_booking(self):

        # Get execution time start
        self.ExecutionTime_Start = time.time()

        self.Timeslots = None
        # Start browser
        Backend.lib.log('Start browser COURSE BOOKING...')
        self.Browser = Backend.lib.CBrowser(Backend.lib.BrowserType.Chrome, Backend.lib.settings)
        self.Timeslots = self.Browser.start_browser_course_booking()

        i = 0
        maxTries = 5
        success = False
        while i < maxTries and not success:
            try:
                # Check if we find free time slot on course
                selectedTimeslot = None
                for key in self.Timeslots:
                    # At first timeslot needs to be free
                    if self.Timeslots[key].IsFree:
                        # Check if time is in range
                        if self.Timeslots[key].Slot >= Backend.lib.settings.Document['round'][0]['timeslot_timespan_start'] and \
                                self.Timeslots[key].Slot <= Backend.lib.settings.Document['round'][0]['timeslot_timespan_end']:
                            selectedTimeslot = self.Timeslots[key]
                            break

                if selectedTimeslot is None:
                    Backend.lib.log_warning('Could not find valid time slot')
                    self.Browser.logout()
                    self.Browser.dispose()
                    return

                Backend.lib.log('Round selected => Timeslot: {0}, Course: {1}, IsFree: {2} '.format(selectedTimeslot.Slot.strftime('%d.%m.%Y - %H:%M'), Backend.lib.settings.Document['courseBooking_enum'].name, selectedTimeslot.IsFree))

                self.Browser.reservation(_timeslot=selectedTimeslot)
                result = self.Browser.partner_reservation(_id=0)
                if result:
                    self.Browser.send_reservation()
                    # TODO: Check if reservation was successful?
                else:
                    Backend.lib.log_warning('Not all partners could be found. Skip reservation')
                success = True
            except Exception as e:
                Backend.lib.log_error('Could not book timeslot: {0}'.format(str(e)))
                # Something went wrong -> Parse again and re-try
                self.Timeslots = None
                self.Timeslots = self.navigate_to_timeslots()
                i = i + 1

        # Get execution time start
        self.ExecutionTime_Stop = time.time()
        Backend.lib.log('Execution time: {}'.format(self.ExecutionTime_Stop - self.ExecutionTime_Start))

        Backend.lib.log('Done... Browser program')
        self.Browser.logout()
        self.Browser.dispose()

    def close_browser(self):
        Backend.lib.log('Close current browser...')
        self.Browser.dispose()

    def endBookingSession(self):
        Backend.lib.log('Execution done')
        # Execution done
        Backend.lib.settings.Document = None

    def pipe_handler(self):
        # Check if new request is available
        if self.Pipe.new_data_available():
            # Get data
            operation, data = self.Pipe.get_data()
            # Handle data
            if operation == PipeOperation.Req_CourseLayout:
                self.Pipe.send_data(PipeOperation.Resp_CourseLayout, self.CourseLayout)
            elif operation == PipeOperation.Req_CourseStatus:
                self.Pipe.send_data(PipeOperation.Resp_CourseStatus, self.CourseStatus)
            elif operation == PipeOperation.Req_ReqInProgress:
                self.Pipe.send_data(PipeOperation.Resp_ReqInProgress, 1 if Backend.lib.settings.Document is not None else 0)
            elif operation == PipeOperation.Req_NewReq:
                Backend.lib.settings.handle_new_data(data)
                self.Pipe.send_data(PipeOperation.Resp_NewReq)
            elif operation == PipeOperation.Req_CancelReq:
                Backend.lib.settings.handle_new_data(None)
                self.Pipe.send_data(PipeOperation.Resp_CancelReq)

        # Send boot message once
        if not self.Booted and self.LastLayoutCheck is not None:
            print('Backend booted')
            self.Pipe.send_data(PipeOperation.BackendBooted)
            self.Booted = True
