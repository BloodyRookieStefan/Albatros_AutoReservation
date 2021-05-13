import time
import re
import datetime

from .progEnums import *
from .basic_actions import CBasicActions
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

class CCourseBooking(CBasicActions):

    def __init__(self):
        pass

    def start_browser_course_booking(self):
        # Load website
        self.Driver.get(self.Settings.Document['weburl_booking'])

        self.login()
        self.booktimes()
        self.set_date()

        # Set course type
        self.set_course(self.Settings.Document['courseBooking_enum'])

        # Refresh until available
        available = False
        while not available:
            table = self.get_timeslotTable()
            if table is not None and len(table) > 0:
                available = True
            else:
                time.sleep(1)
                self.Driver.refresh()

        return self.parse_timeslots()

    def login(self):
        print('Website login...')
        # Set username
        self.set_textbox(_type=By.ID, _tag='user', _sendKeys=self.Settings.Document['username'])
        # Set pwd
        self.set_textbox(_type=By.ID, _tag='password', _sendKeys=self.Settings.Document['password'])
        # CLick login button
        self.click_button(_type=By.CLASS_NAME ,_tag='button')

        # Wait until iFrame "dynamic" is fully loaded
        self.wait_until_tag_is_present(_type=By.ID, _tag='dynamic')

    def booktimes(self):
        # Press Startzeiten
        self.click_button(_type=By.ID, _tag='pr_res_calendar')

    def set_date(self):
        print('Set date: {}'.format(self.Settings.Document['date']))
        self.switch_to_frame(_type=By.ID, _tag='dynamic')
        # Set Date
        self.set_textbox(_type=By.ID, _tag='date', _sendKeys=self.Settings.Document['date'], _keyPress=Keys.ENTER, _options='control+a')

    def set_course(self, _course):
        print('Set course: {}'.format(_course))
        # Set course
        self.set_dropdown(_tag='ro_id', _target=_course)

    def parse_timeslots(self):
        timeslots = dict()

        table = self.get_timeslotTable()
        if len(table) == 0:
            raise Exception('Could not parse timetable')

        tableSplit = table[0].text.split('\n')
        index = 0
        for tSlot in tableSplit:
            btn_text = tSlot.strip()
            if re.search("^[0-9]{1,2}:[0-9]{1,2}$", btn_text):
                if index - 1 > -1:
                    btn_text_BEFORE = tableSplit[index - 1].strip()
                    if re.search("^[0-9]{1,2}:[0-9]{1,2}$", btn_text_BEFORE):
                        # Free
                        timeslots[btn_text] = CTimeslot(_timeVal=[btn_text, self.Settings.Document['date_converted']], _isFree=True)
                    else:
                        # Not free
                        timeslots[btn_text] = CTimeslot(_timeVal=[btn_text, self.Settings.Document['date_converted']], _isFree=False)
                else:
                    #  First element free and it is free
                    timeslots[btn_text] = CTimeslot(_timeVal=[btn_text, self.Settings.Document['date_converted']], _isFree=True)
            index += 1

        # Sort availible timeslots early -> old
        done = False
        tups = list(timeslots.items())
        while not done:
            indexChanged = False
            for i in range(0, len(tups)):
                if i+ 1 < len(tups):
                    hashLowerIndex = tups[i][1].Slot.hour * 100 + tups[i][1].Slot.minute
                    hashUpperIndex = tups[i + 1][1].Slot.hour * 100 + tups[i + 1][1].Slot.minute
                    if hashUpperIndex < hashLowerIndex:
                        tups[i], tups[i + 1] = tups[i + 1], tups[i]
                        indexChanged = True

            # We ran trough all without switching index -> Done
            if not indexChanged:
                done = True;

        return dict(tups)


    def reservation(self, _timeslot):
        # Set timeslot
        self.select_timeslot(_timeslotStr=_timeslot.Str_text)
        # Switch to iFrame
        self.switch_to_frame(_type=By.ID, _tag='calendar_details')
        # Click reservation button
        self.click_button(_type=By.ID, _tag='btnMakeRes')


    def partner_reservation(self, _id):
        print('Partner reservation')
        # Toggle frames??? Without not working?
        self.switch_toDefaultFrame()
        self.switch_to_frame(_type=By.ID, _tag='dynamic')

        # Set partner
        for i in range(0, 4):
            partner = self.Settings.Document['round'][_id]['partner{}'.format(i)][0]
            if partner['firstName'] != 'None' and partner['lastName'] != 'None':
                print('Partner reservation: {} {}'.format(partner['firstName'], partner['lastName']))
                # Set first name
                self.set_textbox(_type=By.NAME, _tag='fname', _sendKeys=partner['firstName'], _options=['control+a'])
                # Set last name
                self.set_textbox(_type=By.NAME, _tag='lname', _sendKeys=partner['lastName'], _options=['control+a'])
                # Click search button
                self.click_button(_type=By.ID, _tag='btnSearch')
                # Get add button and press it. Classification by image
                hits = self.Driver.find_elements(By.CLASS_NAME, 'abutton')
                for hit in hits:
                    if 'img/plus.gif' in hit.get_attribute("src"):
                        hit.click()
                        break

    def send_reservation(self):
        print('Reservation send')
        return
        if not self.Settings.Document['developermode']:
            # Make reservation
            print('Reservation send')
            click_button(_driver=self.Driver, _type=By.ID, _tag='btnNext')
        else:
            print('WARNING: Developer mode active. No reservation send')

    def logout(self):
        self.switch_toDefaultFrame()
        self.click_button(_type=By.ID, _tag='logout')

    ################################################################################## ACTIONS ##################################################################################

    def set_textbox(self, _type, _tag, _sendKeys, _keyPress = Keys.NULL, _options = []):
        # Wait until present
        self.wait_until_tag_is_present(_type=_type, _tag=_tag)
        # Get element by ID
        element = self.Driver.find_element(_type, _tag)
        # Mark text in textbox
        if 'control+a' in _options:
            action = webdriver.ActionChains(self.Driver)
            action.key_down(Keys.LEFT_CONTROL).send_keys_to_element(element, 'a').key_up(Keys.LEFT_CONTROL).perform()
        # Send keys with extra key press at the end or not
        if _keyPress == Keys.NULL:
            element.send_keys(_sendKeys)                                    # Send keys
        else:
            element.send_keys('{} {}'.format(_sendKeys, _keyPress))         # Send keys and press key

    def set_dropdown(self, _tag, _target):
        # Wait until present
        self.wait_until_tag_is_present(_type=By.NAME, _tag=_tag)
        # Get element by name and open it
        element = self.Driver.find_element(By.NAME, _tag)
        element.click()

        # Get up to first entry
        element.send_keys(Keys.UP)
        element.send_keys(Keys.UP)
        element.send_keys(Keys.UP)

        if _target == BookingMode.Eighteen:
            # Press key down
            element.send_keys(Keys.DOWN)
        elif _target == BookingMode.Nine:
            # Press key down
            element.send_keys(Keys.DOWN)
            element.send_keys(Keys.DOWN)
        else:
            raise ValueError('{} is an unknown course'.format(_target))
        element.send_keys(Keys.ENTER)

    def select_timeslot(self, _timeslotStr):
        element = self.get_timeslotByXPath(_timeslotStr)
        if element == None:
            raise ValueError('Could not find timeslot: {}'.format(_timeslotStr.strftime('%H:%M')))
        element.click()

    def get_timeslotByXPath(self, _timeslotStr):
        elements = self.get_allLinks()
        # Find timeslot link
        for element in elements:
            if _timeslotStr == element.text:
                return element
        return None

    def get_timeslotTable(self):
        return self.Driver.find_elements_by_xpath("//*[@id='gridarea']/table/tbody")

class CTimeslot:

    Str_text = None
    Course = None
    Slot = None
    IsFree = False

    def __init__(self, _timeVal, _isFree):

        self.Str_text = _timeVal[0]
        self.IsFree = _isFree

        # Convert timeslot
        timeSplit = _timeVal[0].split(':')
        self.Slot = datetime.datetime(_timeVal[1].year, _timeVal[1].month, _timeVal[1].day, int(timeSplit[0]), int(timeSplit[1]), 0)

