import lib.framework
import re
from .settings import settings
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def wait_until_tag_is_present(_driver, _type, _tag, _to=30):
    WebDriverWait(_driver, _to).until(EC.presence_of_element_located((_type, _tag)))

def switch_to_frame(_driver, _type, _tag):
    _driver.switch_to.frame(_tag)

def switch_toDefaultFrame(_driver):
    _driver.switch_to.default_content()

def set_textbox(_driver, _type, _tag, _sendKeys, _keyPress = Keys.NULL, _options = []):
    # Wait until present
    wait_until_tag_is_present(_driver=_driver, _type=_type, _tag=_tag)
    # Get element by ID
    element = _driver.find_element(_type, _tag)
    # Mark text in textbox
    if 'control+a' in _options:
        action = webdriver.ActionChains(_driver)
        action.key_down(Keys.LEFT_CONTROL).send_keys_to_element(element, 'a').key_up(Keys.LEFT_CONTROL).perform()
    # Send keys with extra key press at the end or not
    if _keyPress == Keys.NULL:
        element.send_keys(_sendKeys)                                    # Send keys
    else:
        element.send_keys('{} {}'.format(_sendKeys, _keyPress))         # Send keys and press key

def set_dropdown(_driver, _tag, _target):
    # Wait until present
    wait_until_tag_is_present(_driver=_driver, _type=By.NAME, _tag=_tag)
    # Get element by name and open it
    element = _driver.find_element(By.NAME, _tag)
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
    if element == None:
        raise ValueError('Could not find timeslot: {}'.format(_timeslot.strftime('%H:%M')))
    element.click()

def get_timeslotByXPath(_driver, _timeslot):
    elements = _driver.find_elements_by_xpath("//a[@href]")
    timeslotFormatted = _timeslot.strftime('%H:%M')

    for element in elements:
        if timeslotFormatted == element.text:
            return element

    return None

def check_timeslot(_driver, _timeslot):
    select_timeslot(_driver=_driver, _timeslot=_timeslot)
    switch_to_frame(_driver=_driver, _type=By.ID, _tag='calendar_details')
    element = _driver.find_elements_by_xpath("//td[contains(.,'Slot gebucht')]")
    if element != []:
        return -1, 'Slot full'
    element = _driver.find_elements_by_xpath("//td[contains(.,'Gestartet')]")
    if element != []:
        return -1, 'Slot already started'
    element = _driver.find_elements_by_xpath("//div/table/tbody/tr/td/div")
    if element != []:
        return -1, 'Slot has already booked member'
    return 0, ''

def click_button(_driver, _type, _tag):
    # Get button by class name and click
    _driver.find_element(_type, _tag).click()