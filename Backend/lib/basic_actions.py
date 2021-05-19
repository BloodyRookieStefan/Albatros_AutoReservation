'''
#############################################################################################
@brief Collection of basic browser actions and functions
#############################################################################################
'''

from .progEnums import *
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class CBasicActions():

    def __init__(self):
        pass

    def click_button(self, _type, _tag):
        button = self.Driver.find_element(_type, _tag)
        if button.isEnabled():
            # Get button by class name and click
            self.Driver.find_element(_type, _tag).click()
        else:
            raise Exception('Button {0} is disabled'.format(_tag))

    def refresh(self):
        self.Driver.refresh()

    def switch_to_frame(self, _type, _tag):
        self.Driver.switch_to.frame(_tag)

    def switch_toDefaultFrame(self):
        self.Driver.switch_to.default_content()

    def wait_until_tag_is_present(self, _type, _tag, _to=30):
        WebDriverWait(self.Driver, _to).until(EC.presence_of_element_located((_type, _tag)))

    def get_allLinks(self):
        return self.Driver.find_elements_by_xpath("//a[@href]")

    def course_name_to_enum(self, _text):
        _text = _text.replace(' ', '').lower()
        if _text == 'gelb/rot':
            return CourseType.Yellow_Red
        elif _text == 'gelb/blau':
            return CourseType.Yellow_Blue
        elif _text == 'rot/gelb':
            return CourseType.Red_Yellow
        elif _text == 'rot/blau':
            return CourseType.Red_Blue
        elif _text == 'blau/rot':
            return CourseType.Blue_Red
        elif _text == 'blau/gelb':
            return CourseType.Blue_Yellow
        elif _text == 'gelb':
            return CourseType.Yellow
        elif _text == 'blau':
            return CourseType.Blue
        elif _text == 'rot':
            return CourseType.Red
        else:
            raise Exception('Failed to parse course type: {0}'.format(_text))