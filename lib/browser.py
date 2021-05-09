'''
#############################################################################################
@brief Browser object to control browser
@param self.Driver - Selenium browser object
@param self.Settings - Parsed *.yaml setting file
#############################################################################################
'''

import os

from selenium import webdriver
from .course_booking import CCourseBooking
from .course_layout import CCourseLayout
from.progEnums import BrowserType

class CBrowser(CCourseBooking, CCourseLayout):

    Mode = None
    Driver = None
    Settings = None

    def __init__(self, _type, _settings):

        self.Settings = _settings
        optionsList = ['--incognito']

        directorypath = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))

        if _type == BrowserType.Chrome:
            options = webdriver.ChromeOptions()
            if self.Settings.Document['workspace'].lower() == 'windows':
                options.add_argument('{0}\chromedriver.exe'.format(directorypath))
            elif self.Settings.Document['workspace'].lower() == 'Linux':
                options.add_argument('{0}\chromedriver'.format(directorypath))
            else:
                raise Exception('{} is an unkown workspace'.format(self.Settings.Document['workspace']))

            for option in optionsList:
                options.add_argument(option)

            self.Driver = webdriver.Chrome(options=options)
            self.Driver.maximize_window()
        else:
            raise Exception('Unknown browser')

    def dispose(self):
        try:
            self.Driver.quit()
        except:
            pass
        self.Driver = None

