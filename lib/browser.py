import os
import time
from .browser_actions import *
from .timeslot import timeslot
from enum import Enum
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

class BrowserType(Enum):
    Chrome = 0

class CBrowser():

    Driver = None
    Settings = None

    def __init__(self, _type, _settings):

        self.Settings = _settings
        optionsList = ['--incognito']

        directorypath = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))

        if _type == BrowserType.Chrome:
            options = webdriver.ChromeOptions()

            if self.Settings.Document['workspace'] == 'Windows':
                options.add_argument('{}\chromedriver.exe'.format(directorypath))
            elif self.Settings.Document['workspace'] == 'Linux':
                options.add_argument('{}\chromedriver'.format(directorypath))
            else:
                raise ValueError('{} is an unkown workspace'.format(self.Settings.Document['workspace']))

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
        print('Website login...')
        # Load website
        self.Driver.get(self.Settings.Document['weburl'])
        # Set username
        set_textbox(_driver=self.Driver, _type=By.ID, _tag='user', _sendKeys=self.Settings.Document['username'])
        # Set pwd
        set_textbox(_driver=self.Driver, _type=By.ID, _tag='password', _sendKeys=self.Settings.Document['password'])
        # CLick login button
        click_button(_driver=self.Driver, _type=By.CLASS_NAME,_tag='button')

        # Wait until iFrame "dynamic" is fully loaded
        wait_until_tag_is_present(_driver=self.Driver, _type=By.ID, _tag='dynamic')

    def refresh(self):
        self.Driver.refresh()

    def booktimes(self):
        # Press Startzeiten
        click_button(_driver=self.Driver, _type=By.ID, _tag='pr_res_calendar')

    def res_timeslots_available(self, _id):
        switch_to_frame(_driver=self.Driver, _type=By.ID, _tag='dynamic')
        element = get_timeslotByXPath(_driver=self.Driver, _timeslot=self.Settings.Document['round'][_id]['timeslot_converted'])
        if element is None:
            return False
        else:
            return True

    def set_date(self):
        print('Set date: {}'.format(self.Settings.Document['date']))
        switch_to_frame(_driver=self.Driver, _type=By.ID, _tag='dynamic')
        # Set Date
        set_textbox(_driver=self.Driver, _type=By.ID, _tag='date', _sendKeys=self.Settings.Document['date'], _keyPress=Keys.ENTER, _options='control+a')

    def set_course(self, _course):
        print('Set course: {}'.format(_course))
        # Set course
        set_dropdown(_driver=self.Driver, _tag='ro_id', _target=_course.lower())

    def parse_timeslots(self, _course):
        timeslots = dict()

        elements = get_allLinks(_driver=self.Driver)
        for element in elements:
            btn_class = element.get_attribute('class')

            if btn_class != 'c-basic-txt':
                continue    # Link is not timeslot link

            btn_text = element.get_attribute('text')
            timeslots[btn_text] = timeslot(_class=btn_class, _timeVal=[btn_text, self.Settings.Document['date_converted']], _linkElement=element, _course=_course)

        return timeslots

    def reservation(self, _id):
        print('Booking time found. Start reservation: {}'.format(self.Settings.Document['round'][_id]['timeslot_converted'].strftime("%H:%M:%S")))
        # Set timeslot
        select_timeslot(_driver=self.Driver, _timeslot=self.Settings.Document['round'][_id]['timeslot_converted'])
        # Switch to iFrame
        switch_to_frame(_driver=self.Driver, _type=By.ID, _tag='calendar_details')
        # Click reservation button
        click_button(_driver=self.Driver, _type=By.ID, _tag='btnMakeRes')

    def partner_reservation(self, _id):
        # Toggle frames??? Without not working?
        switch_toDefaultFrame(_driver=self.Driver)
        switch_to_frame(_driver=self.Driver, _type=By.ID, _tag='dynamic')

        # Set partner
        for i in range(0, 4):
            partner = self.Settings.Document['round'][_id]['partner{}'.format(i)][0]
            if partner['firstName'] != 'None' and partner['lastName'] != 'None':
                print('Partner reservation: {} {}'.format(partner['firstName'], partner['lastName']))
                # Set first name
                set_textbox(_driver=self.Driver, _type=By.NAME, _tag='fname', _sendKeys=partner['firstName'])
                # Set last name
                set_textbox(_driver=self.Driver, _type=By.NAME, _tag='lname', _sendKeys=partner['lastName'])
                # Click search button
                click_button(_driver=self.Driver, _type=By.ID, _tag='btnSearch')

    def send_reservation(self):
        if not self.Settings.Document['developermode']:
            # Make reservation
            print('Reservation send')
            click_button(_driver=self.Driver, _type=By.ID, _tag='btnNext')
        else:
            print('WARNING: Developer mode active. No reservation send')

    def move_default(self):
        switch_toDefaultFrame(_driver=self.Driver)

    def logout(self):
        switch_toDefaultFrame(_driver=self.Driver)
        click_button(_driver=self.Driver, _type=By.ID, _tag='logout')