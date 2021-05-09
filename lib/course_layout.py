
from .progEnums import *
from .basic_actions import CBasicActions

from selenium.webdriver.common.by import By

class CCourseLayout(CBasicActions):

    CourseLayout = dict()

    def __init__(self):
        pass

    def start_browser_course_layout(self):
        self.Mode = BrowserMode.CourseLayout

        # Load website
        self.Driver.get(self.Settings.Document['weburl_layout'])

        # Parse course layout
        self.parse_course_layout()

    def parse_course_layout(self):
        # Clear dict
        self.CourseLayout = dict()
        # Wait until loaded
        self.wait_until_tag_is_present(_type=By.ID, _tag='tablepress-1')
        # Get table
        tableEntries = self.Driver.find_elements_by_xpath("//*[@id='tablepress-1']/tbody/tr/td")
        # Parse table
        i = 0
        for entry in tableEntries:
            if i == 0:
                day = entry.text
            elif i == 1:
                date = entry.text
            elif i == 2:
                course18 = self.course_name_to_enum(entry.text)
            elif i == 3:
                course9 = self.course_name_to_enum(entry.text)
            elif i == 4:
                pinPos = entry.text
            elif i == 5:
                spacer = entry.text
            elif i == 6:
                commet = entry.text
                self.CourseLayout[date] = Layout(day, date, course18, course9, pinPos, spacer, commet)
                i = -1

            i = i + 1

class Layout:

    Day = None
    Date = None
    Course18 = None
    Course9 = None
    PinPos = None
    Spacer = ''
    Comment = ''

    def __init__(self, _day, _date, _course18, _course9, _pinPos, _spacer, _comment):
        self.Day = _day
        self.Date = _date
        self.Course18 = _course18
        self.Course9 = _course9
        self.PinPos = _pinPos
        self.Spacer = _spacer
        self.Comment = _comment
