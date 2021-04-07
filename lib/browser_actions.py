import lib.framework
import re
from .settings import settings
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

def set_textboxByID(_driver, _id, _sendKeys, _keyPress = Keys.NULL, _options = []):
    # Get element by ID
    element = _driver.find_element_by_id(_id)
    # Mark text in textbox
    if 'control+a' in _options:
        action = webdriver.ActionChains(_driver)
        action.key_down(Keys.LEFT_CONTROL).send_keys_to_element(element, 'a').key_up(Keys.LEFT_CONTROL).perform()
    # Send keys with extra key press at the end or not
    if _keyPress == Keys.NULL:
        element.send_keys(_sendKeys)                                    # Send keys
    else:
        element.send_keys('{} {}'.format(_sendKeys, _keyPress))         # Send keys and press key
    # Debug
    if settings.Document['developmode']:
        print('Send (set_textboxByID): {} {}'.format(_sendKeys, _keyPress))

def set_textboxByName(_driver, _name, _sendKeys):
    # Get element by ID
    element = _driver.find_element_by_name(_name)
    element.send_keys(_sendKeys)
    # Debug
    if settings.Document['developmode']:
        print('Send (set_textboxByName): {}'.format(_sendKeys))

def set_dropdownCourseByName(_driver, _name, _target):

    # Get element by name and open it
    element = _driver.find_element_by_name(_name)
    element.click()

    # Get up to first entry
    element.send_keys(Keys.UP)
    element.send_keys(Keys.UP)
    element.send_keys(Keys.UP)

    if _target == 'gelb':
        # Press key down
        element.send_keys(Keys.DOWN)
    elif _target == 'rot':
        # Press key down
        element.send_keys(Keys.DOWN)
        element.send_keys(Keys.DOWN)
    elif _target == 'blau':
        # Press key down
        element.send_keys(Keys.DOWN)
        element.send_keys(Keys.DOWN)
        element.send_keys(Keys.DOWN)
    else:
        raise ValueError('{} is an unknown course'.format(_target))
    element.send_keys(Keys.ENTER)

def select_timeslot(_driver, _timeslot):
    element = get_timeslotByXPath(_driver, _timeslot)
    element.click()
    # Debug
    if settings.Document['developmode']:
        print('Send (select_timeslot): {}'.format(_timeslot.strftime('%H:%M')))


def check_timeslotIsFree(_driver, _timeslot):
    element = get_timeslotByXPath(_driver, _timeslot)

def get_timeslotByXPath(_driver, _timeslot):
    elements = _driver.find_elements_by_xpath("//a[@href]")
    timeslotFormatted = _timeslot.strftime('%H:%M')

    for element in elements:
        if timeslotFormatted == element.text:
            # Debug
            if settings.Document['developmode']:
                print('Timeslot found: {} on {}'.format(timeslotFormatted, _timeslot.strftime('%d.%m.%Y')))
            return element

    raise ValueError('Could not find timeslot: {}'.format(timeslotFormatted))

def click_buttonByClassName(_driver, _className):
    # Get button by class name and click
    _driver.find_element_by_class_name(_className).click()
    # Debug
    if settings.Document['developmode']:
        print('Send (click_buttonByClassName): {}'.format(_className))

def click_buttonByID(_driver, _id):
    # Get button by class name and click
    _driver.find_element_by_id(_id).click()
    # Debug
    if settings.Document['developmode']:
        print('Send (click_buttonByID): {}'.format(_id))

def switch_toIFrame(_driver, _iFrame):
    # Find iFrame by div name
    iframe = _driver.find_element_by_css_selector("#{} > iframe".format(_iFrame))
    # Switch to iFrame
    _driver.switch_to.frame(iframe)
    #Debug
    if settings.Document['developmode']:
        print('Send (switch_toIFrame): {}'.format(_iFrame))

def switch_toDefaultFrame(_driver):
    _driver.switch_to.default_content()

