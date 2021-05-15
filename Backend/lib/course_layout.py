'''
#############################################################################################
@brief Browser functions for course layout
@param self.FilePath - Path where the layout file should be generated
#############################################################################################
'''

import os
import yaml

from .logging import log, log_warning, log_error
from .basic_actions import CBasicActions
from selenium.webdriver.common.by import By

class CCourseLayout(CBasicActions):

    FilePath = ''

    def __init__(self):
        pass

    def start_browser_course_layout(self):
        self.FilePath = '{}/latestCourseLayout.yaml'.format(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

        # Load website
        self.Driver.get('https://golfclubliebenstein.de/platzbenutzung')

        # Parse course layout
        return self.parse_course_layout()

    def parse_course_layout(self):
        # Setup dict
        courseLayout = dict()
        # Wait until loaded
        self.wait_until_tag_is_present(_type=By.ID, _tag='tablepress-1')
        # Get table
        tableEntries = self.Driver.find_elements_by_xpath("//*[@id='tablepress-1']/tbody/tr/td")
        # Parse table
        i = 0
        for entry in tableEntries:
            if i == 0:
                day = entry.text
            elif i == 1:
                date = entry.text
            elif i == 2:
                 course18 = entry.text
            elif i == 3:
                 course9 = entry.text
            elif i == 4:
                pinPos = entry.text
            elif i == 5:
                comment = entry.text
                # Only if we could parse the information create entry
                if course9 != '' and course18 != '':
                    courseLayout[date] = CLayout(day, date, course18, course9, pinPos, comment)
                i = -1

            i = i + 1

        self.write_to_disk(courseLayout)

    def write_to_disk(self, _dict):
        # Remove old layout
        if os.path.exists(self.FilePath):
            os.remove(self.FilePath)

        # Create dict we can save without python objects
        target = dict()
        for date in _dict:
            target[date] = {'date':date, 'day':_dict[date].Day, 'course18':_dict[date].Course18_Text, 'course9':_dict[date].Course9_Text, 'pinpos':_dict[date].PinPos, 'comment':_dict[date].Comment}

        # Save new course layout
        with open(self.FilePath, 'w') as file:
            yaml.dump(target, file, default_flow_style=False)

class CLayout(CBasicActions):

    Day = None
    Date = None
    Course18 = None
    Course18_Text = None
    Course9 = None
    Course9_Text = None
    PinPos = None
    Comment = ''

    def __init__(self, _day, _date, _course18, _course9, _pinPos, _comment):
        self.Day = _day
        self.Date = _date
        self.Course18 = self.course_name_to_enum(_course18)
        self.Course18_Text = _course18
        self.Course9 = self.course_name_to_enum(_course9)
        self.Course9_Text = _course9
        self.PinPos = _pinPos
        self.Comment = _comment
