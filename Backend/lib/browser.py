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
from .weather_forecast import CWheaterForecast
from .progEnums import BrowserType, OperatingSystem


class CBrowser(CCourseBooking, CCourseLayout, CWheaterForecast):
    Driver = None
    Settings = None

    def __init__(self, _type, _settings):

        self.Settings = _settings
        optionsList = ['--incognito']

        directorypath = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))

        if _type == BrowserType.Chrome:
            options = webdriver.ChromeOptions()
            for option in optionsList:
                options.add_argument(option)

            if self.Settings.Workspace == OperatingSystem.Windows:
                self.Driver = webdriver.Chrome(executable_path='{0}/chromedriver.exe'.format(directorypath, options=options))
            elif self.Settings.Workspace == OperatingSystem.Linux:
                self.Driver = webdriver.Chrome(options=options)
            else:
                raise Exception('{} is an unknown workspace'.format(self.Settings.Document['workspace']))


            #self.Driver = webdriver.Chrome(options=options)
        else:
            raise Exception('Unknown browser')

        self.Driver.maximize_window()

    def dispose(self):
        try:
            self.Driver.quit()
        except:
            pass
        self.Driver = None
