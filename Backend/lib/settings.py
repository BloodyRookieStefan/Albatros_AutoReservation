'''
#############################################################################################
@brief Contains parsed settings.yaml
@param self.FilePath - Path to *.yaml file
@param self.Document - Read document
#############################################################################################
'''

import yaml
import os
import sys

from datetime import datetime, timedelta
from .progEnums import *

class CSettings:

    FilePath = ''
    Size = None
    Document = None
    Workspace = None

    def __init__(self):
        # Build settings path
        self.FilePath = '{}/settings.yaml'.format(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
        if sys.platform == 'win32':
            self.Workspace = OperatingSystem.Windows
        elif sys.platform == 'linux':
            self.Workspace = OperatingSystem.Linux
        else:
            raise ValueError('Unkown operating system: {0}'.format(sys.platform))

    def read(self):
        # Check if file exists
        if not os.path.exists(self.FilePath):
            raise ValueError('{} file not found'.format(self.FilePath))
        # Read settings
        with open(self.FilePath, 'r') as file:
            self.Document = yaml.safe_load(file)
        # Convert time values
        self.convert_time_values()

        self.Size = os.path.getsize(self.FilePath)

    def sizeHasChanged(self):
        if os.path.exists(self.FilePath):
            if self.Size != os.path.getsize(self.FilePath):
                return True
            else:
                return False
        else:
            return False

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