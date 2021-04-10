import yaml
import os
import datetime

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

        hour = int(self.Document['executetime_h'])
        minute = int(self.Document['executetime_m'])
        second = int(self.Document['executetime_s'])

        self.Document['executiontime_converted'] = datetime.datetime(year, month, day, hour, minute, second)

        # Convert timeslot times
        for round in self.Document['round']:
            day = int(round['date'].split('.')[0])
            month = int(round['date'].split('.')[1])
            year = int(round['date'].split('.')[2])

            hour = int(round['timeslot_h'])
            minute = int(round['timeslot_m'])
            round['timeslot_converted'] = datetime.datetime(year, month, day, hour, minute, 0)

settings = CSettings()