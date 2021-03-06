'''
#############################################################################################
@brief Browser functions for course layout and course status
#############################################################################################
'''

import os
import yaml
import re

from .logging import log, log_warning, log_error
from .basic_actions import CBasicActions
from datetime import datetime
from selenium.webdriver.common.by import By

class CCourseLayout(CBasicActions):

    def __init__(self):
        pass

    def start_browser_course_layout(self):
        # Load website
        self.Driver.get(self.Settings.TemplateDocument['weburl_crs_layout'])
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
                matchPattern = re.search("^[^0-9]*([0-9]{1,2}\.[0-9]{1,2}\.[0-9]{4}).*$", entry.text)
                if matchPattern is not None:
                    date = matchPattern.group(1)
                else:
                    date = None
            elif i == 2:
                 course18 = entry.text
            elif i == 3:
                 course9 = entry.text
            elif i == 4:
                pinPos = entry.text
            elif i == 5:
                comment = entry.text
                # Only if we could parse the information create entry
                if course9 != '' and course18 != '' and date is not None:
                    courseLayout[date] = CLayout(day, date, course18, course9, pinPos, comment)
                else:
                    log_warning('Could not parse date. Storage condition not met')
                i = -1

            i = i + 1

        lastLayoutUpdate = datetime.now()
        # Create dict we can save without python objects
        target = dict()
        for date in courseLayout:
            target[date] = {'date':date,
                            'day':courseLayout[date].Day,
                            'course18':courseLayout[date].Course18_Text,
                            'course9':courseLayout[date].Course9_Text,
                            'pinpos':courseLayout[date].PinPos,
                            'comment':courseLayout[date].Comment,
                            'timestamp':lastLayoutUpdate}

        return target

    # ----------------------------------------------------------

class CCourseStatus(CBasicActions):

    def __init__(self):
        pass

    def start_browser_course_status(self):
        # Load website
        self.Driver.get(self.Settings.TemplateDocument['weburl_crs_status'])

        # Parse course status
        return self.parse_course_status()

    def parse_course_status(self):
        # Setup dict
        courseStatus = dict()
        # Wait until loaded
        self.wait_until_tag_is_present(_type=By.ID, _tag='tablepress-2')
        # Get table
        tableEntries = self.Driver.find_elements_by_xpath("//*[@id='tablepress-2']/tbody/tr/td")

        i = 0
        for entry in tableEntries:
            if i == 1:
                courseStatus['YELLOW'] = entry.text
            elif i == 3:
                courseStatus['RED'] = entry.text
            elif i == 5:
                courseStatus['BLUE'] = entry.text
            elif i > 5:
                break

            i = i + 1

        # Set last course status update to now
        courseStatus['timestamp'] = datetime.now()

        return courseStatus

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
