'''
#############################################################################################
@brief Functions to control settings.yaml
@param self.Size - Size document
@param self.Document - Read document
@param self.Workspace - Program environment Linux/Windows
#############################################################################################
'''

import yaml
import os
import sys

from datetime import datetime, timedelta
from .progEnums import *

class CSettings:

    Size = None
    Document = None
    Workspace = None

    def __init__(self):
        if sys.platform == 'win32':
            self.Workspace = OperatingSystem.Windows
        elif sys.platform == 'linux':
            self.Workspace = OperatingSystem.Linux
        else:
            raise ValueError('Unkown operating system: {0}'.format(sys.platform))

    def handle_new_data(self, _data):
        self.Document = None
        if _data is not None:
            self.Document = _data
            self.convert_time_values()

    def convert_time_values(self):
        # Calc execution date based on execution span
        datetime.now() + timedelta(days=self.Document['executespan'])

        hour = int(self.Document['executetime'].split('-')[0])
        minute = int(self.Document['executetime'].split('-')[1])

        # Convert book date
        day = int(self.Document['date'].split('.')[0])
        month = int(self.Document['date'].split('.')[1])
        year = int(self.Document['date'].split('.')[2])
        self.Document['date_converted'] = datetime(year, month, day, 0, 0, 0)
        self.Document['courseBooking_enum'] = BookingMode(self.Document['courseBooking'])

        earliestBookingDate = self.Document['date_converted'] - timedelta(days=self.Document['executespan'])
        self.Document['executiontime_converted'] = datetime(earliestBookingDate.year, earliestBookingDate.month, earliestBookingDate.day, hour, minute, 0)

        # -------------------------------------------------
        # Convert timeslot times
        for r in self.Document['round']:
            hour = int(r['start_timeslot'].split('-')[0])
            minute = int(r['start_timeslot'].split('-')[1])
            r['timeslot_timespan_start'] = datetime(year, month, day, hour, minute, 0)

            hour = int(r['end_timeslot'].split('-')[0])
            minute = int(r['end_timeslot'].split('-')[1])
            r['timeslot_timespan_end'] = datetime(year, month, day, hour, minute, 0)
        # -------------------------------------------------

settings = CSettings()