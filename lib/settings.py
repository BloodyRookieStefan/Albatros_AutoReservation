import yaml
import os
import datetime

from enum import Enum

class CourseType(Enum):
    Invalid = 0
    Blue = 1
    Red = 2
    Yellow = 3
    Any = 4

class CSettings:

    FilePath = ''
    Document = None

    def __init__(self):
        # Build settings path
        self.FilePath = '{}\\settings.yaml'.format(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
        # Check if file exists
        if not os.path.exists(self.FilePath):
            raise ValueError('{} file not found'.format(self.FilePath))
        # Read settings
        with open(self.FilePath, 'r') as file:
            self.Document = yaml.safe_load(file)
        # Convert time values
        self.convert_time_values()

    def convert_time_values(self):
        # Convert execution time
        day = int(self.Document['executedate'].split('.')[0])
        month = int(self.Document['executedate'].split('.')[1])
        year = int(self.Document['executedate'].split('.')[2])

        hour = int(self.Document['executetime'].split('-')[0])
        minute = int(self.Document['executetime'].split('-')[1])
        second = int(self.Document['executetime'].split('-')[2])

        self.Document['executiontime_converted'] = datetime.datetime(year, month, day, hour, minute, second)

        # Convert round delay
        hour = int(self.Document['roundMINdelay'].split('-')[0])
        minute = int(self.Document['roundMINdelay'].split('-')[1])
        self.Document['roundMINdelay_converted'] = datetime.datetime(year, month, day, hour, minute, 0)

        hour = int(self.Document['roundMAXdelay'].split('-')[0])
        minute = int(self.Document['roundMAXdelay'].split('-')[1])
        self.Document['roundMAXdelay_converted'] = datetime.datetime(year, month, day, hour, minute, 0)

        # Convert book date
        day = int(self.Document['date'].split('.')[0])
        month = int(self.Document['date'].split('.')[1])
        year = int(self.Document['date'].split('.')[2])

        self.Document['date_converted'] = datetime.datetime(year, month, day, 0, 0, 0)

        # Convert timeslot times
        for r in self.Document['round']:
            hour = int(r['start_timeslot'].split('-')[0])
            minute = int(r['start_timeslot'].split('-')[1])
            r['timeslot_timespan_start'] = datetime.datetime(year, month, day, hour, minute, 0)

            hour = int(r['end_timeslot'].split('-')[0])
            minute = int(r['end_timeslot'].split('-')[1])
            r['timeslot_timespan_end'] = datetime.datetime(year, month, day, hour, minute, 0)

            if r['course'].lower() == 'blue':
                r['course_enum'] = CourseType.Blue
            elif r['course'].lower() == 'red':
                r['course_enum'] = CourseType.Red
            elif r['course'].lower() == 'yellow':
                r['course_enum'] = CourseType.Yellow
            elif r['course'].lower() == 'any':
                r['course_enum'] = CourseType.Any
            else:
                r['course_enum'] = CourseType.Invalid

settings = CSettings()