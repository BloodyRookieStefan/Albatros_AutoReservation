
from .progEnums import *
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class CBasicActions():

    def __init__(self):
        pass

    def click_button(self, _type, _tag):
        # Get button by class name and click
        self.Driver.find_element(_type, _tag).click()

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
        if _text == 'GELB / ROT':
            return CourseType.Yellow_Red
        elif _text == 'GELB / BLAU':
            return CourseType.Yellow_Blue
        elif _text == 'ROT / GELB':
            return CourseType.Red_Yellow
        elif _text == 'ROT / BLAU':
            return CourseType.Red_Blue
        elif _text == 'BLAU / ROT':
            return CourseType.Blue_Red
        elif _text == 'BLAU / GELB':
            return CourseType.Blue_Yellow
        elif _text == 'GELB':
            return CourseType.Yellow
        elif _text == 'BLAU':
            return CourseType.Blue
        elif _text == 'ROT':
            return CourseType.Red
        else:
            raise Exception('Failed to parse course type: {0}'.format(_text))