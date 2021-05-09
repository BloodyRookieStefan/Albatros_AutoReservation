from enum import Enum

class BrowserType(Enum):
    Chrome = 0

class BrowserMode(Enum):
    CourseBooking = 0
    CourseLayout = 1

class CourseType(Enum):
    # Invalid
    Invalid = -1

    Blue = 1
    Red = 2
    Yellow = 3

    Yellow_Red = 10
    Yellow_Blue = 11

    Red_Yellow = 20
    Red_Blue = 21

    Blue_Yellow = 30
    Blue_Red = 31

    Any = 99