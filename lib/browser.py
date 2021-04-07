import os
import lib.framework
from .browser_actions import *
from .settings import settings
from enum import Enum
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

class BrowserType(Enum):
    Chrome = 0,

class CBrowser():

    Driver = None

    def __init__(self, type):

        optionsList = ['--incognito']

        directorypath = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))

        if type == BrowserType.Chrome:
            options = webdriver.ChromeOptions()

            if settings.Document['workspace'] == 'Windows':
                options.add_argument('{}\chromedriver.exe'.format(directorypath))
            elif settings.Document['workspace'] == 'Linux':
                options.add_argument('{}\chromedriver'.format(directorypath))
            else:
                raise ValueError('{} is an unkown workspace'.format(settings.Document['workspace']))

            for option in optionsList:
                options.add_argument(option)

            self.Driver = webdriver.Chrome(options=options)
            self.Driver.maximize_window()
        else:
            raise ValueError('Unknown browser')

    def dispose(self):
        self.Driver.close()
        self.Driver = None

    def login(self):
        # Load website
        self.Driver.get(settings.Document['weburl'])
        # Set username
        set_textboxByID(_driver=self.Driver, _id='user', _sendKeys=settings.Document['username'])
        # Set pwd
        set_textboxByID(_driver=self.Driver, _id='password', _sendKeys=settings.Document['password'])
        # CLick login button
        click_buttonByClassName(_driver=self.Driver, _className='button')

    def booktimes(self):
        # Back to default frame
        switch_toDefaultFrame(_driver=self.Driver)
        # Press Startzeiten
        click_buttonByID(_driver=self.Driver, _id='pr_res_calendar')

    def reservation(self, _id):
        # TODO: Check that all timeslots are free we want to book
        # Switch to iFrame
        switch_toIFrame(_driver=self.Driver, _iFrame='mainDynamicFrameArea')
        # Set Date
        set_textboxByID(_driver=self.Driver, _id='date', _sendKeys=settings.Document['round'][_id]['date'], _keyPress=Keys.ENTER, _options='control+a')
        # Set course
        set_dropdownCourseByName(_driver=self.Driver, _name='ro_id', _target=settings.Document['round'][_id]['course'].lower())
        # Set timeslot
        select_timeslot(_driver=self.Driver, _timeslot=settings.Document['round'][_id]['timeslot_converted'])
        # Switch to iFrame
        switch_toIFrame(_driver=self.Driver, _iFrame='calendarDetailsDiv')
        # Click reservation button
        click_buttonByID(_driver=self.Driver, _id='btnMakeRes')

    def partner_reservation(self, _id):
        # Back to default frame
        switch_toDefaultFrame(_driver=self.Driver)
        # Switch to iFrame
        switch_toIFrame(_driver=self.Driver, _iFrame='mainDynamicFrameArea')
        # Set partner
        for i in range(0, 4):
            partner = settings.Document['round'][_id]['partner{}'.format(i)][0]
            if partner['firstName'] != 'None' and partner['lastName'] != 'None':
                # Set first name
                set_textboxByName(_driver=self.Driver, _name='fname', _sendKeys=partner['firstName'])
                # Set last name
                set_textboxByName(_driver=self.Driver, _name='lname', _sendKeys=partner['lastName'])
                # Click search button
                click_buttonByID(_driver=self.Driver, _id='btnSearch')

    def send_reservation(self):
        pass
        # Make reservation
        #click_buttonByID(_driver=self.Driver, _id='btnNext')

    def logout(self):
        pass