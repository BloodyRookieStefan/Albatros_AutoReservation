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

    def regExMatch(self, input, regex, group, failLog=True):
        regMatch = re.search(regex, input)
        if regMatch:
            return re.search(regex, input).group(group)
        else:
            if failLog:
                log_warning(f'Regex error: "{input}" does not match regex "{regex}" with group "{group}"')
            return None

    def start_browser_course_layout(self):
        # Load website
        self.Driver.get(self.Settings.TemplateDocument['weburl_crs_layout'])
        # Parse course layout
        return self.parse_course_layout()

    def parse_course_layout(self):
        # Setup dict
        courseLayout = dict()
        # Get timestamp
        lastLayoutUpdate = datetime.now()
        # Wait until loaded
        self.wait_until_tag_is_present(_type=By.ID, _tag='platzbelegungPreview')
        # Get table
        table = self.Driver.find_elements(by=By.XPATH, value="//div[@id='platzbelegungPreview']/div[@class='inside']/div[@class='belegung voll']")
        # Run trough all entries
        i = 0
        for entry in table:
            i += 1

            # Parse day/date and pin
            datePin = entry.find_elements(by=By.XPATH, value=".//div[@class='row datePin']")
            if len(datePin) == 1:
                day = self.regExMatch(input=datePin[0].text, regex='^([aA-zZ]+),', group=0)
                date = self.regExMatch(input=datePin[0].text, regex='([0-9]+\.[0-9]+\.[0-9]+)', group=0)
                pinpos = self.regExMatch(input=datePin[0].text, regex='\nPin: ([0-9]+)', group=0)
            else:
                log_warning(f'Unexpected length for datePin "{len(datePin)}"')

            # Extract course and comments
            rowNine = entry.find_elements(by=By.XPATH, value=".//div[@class='row platz nine']")
            if len(rowNine) == 1:
                course9 = self.regExMatch(input=rowNine[0].text, regex=': ([aA-zZ]+)', group=0)
                comment9 = self.regExMatch(input=rowNine[0].text, regex='\n(.*)$', group=0, failLog=False)
            else:
                log_warning(f'Unexpected length for row 9 "{len(rowNine)}"')
            rowEighteen = entry.find_elements(by=By.XPATH, value=".//div[@class='row platz eighteen']")
            if len(rowEighteen) == 1:
                course18 = self.regExMatch(input=rowEighteen[0].text, regex=': ([aA-zZ]+[ ][aA-zZ]+)', group=0)
                comment18 = self.regExMatch(input=rowEighteen[0].text, regex='\n(.*)$', group=0, failLog=False)
            else:
                log_warning(f'Unexpected length for row 9 "{len(rowEighteen)}"')

            # When one of these could not be parsed => Skipp
            if date is None or course9 is None or course18 is None:
                continue

            courseLayout[date] = {'date': date,
                                  'day': day,
                                  'course9': course9,
                                  'course18': course18,
                                  'pinpos': pinpos,
                                  'commentNine': comment9,
                                  'commentEighteen': comment18,
                                  'timestamp': lastLayoutUpdate}

        return courseLayout

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
        self.wait_until_tag_is_present(_type=By.ID, _tag='homePlatzinfos')

        # Extract information from table by using xPath
        xPathToTable = "//div[@id='homePlatzinfos']/div/div[@class='mid full container']"
        xPathToTable_Nine = f"{xPathToTable}/div[@class='entry half loch neunLoch sommer']/div[@class='description']"
        tableNine = self.Driver.find_elements_by_xpath(xPathToTable_Nine)
        textNine = tableNine[0].text

        xPathToTable_Eighteen = f"{xPathToTable}/div[@class='entry half loch achtzehnLoch sommer']/div[@class='description']"
        tableEighteen = self.Driver.find_elements_by_xpath(xPathToTable_Eighteen)
        textEighteen = tableEighteen[0].text

        # Save text from website
        courseStatus['NINE'] = textNine
        courseStatus['EIGHTEEN'] = textEighteen

        # Set last course status update to now
        courseStatus['timestamp'] = datetime.now()

        return courseStatus