import lib
import time
import random

from datetime import datetime
from lib.settings import CourseType


class ExecutionController:

    ExecutionTime_Start = None
    Browser = None

    Timeslots_blue = dict()
    Timeslots_red = dict()
    Timeslots_yellow = dict()

    def __init__(self):
        pass

    def run(self):

        # Pre check if any valid course is set
        if lib.settings.Document['round'][0]['course_enum'] == CourseType.Invalid and lib.settings.Document['round'][1]['course_enum'] == CourseType.Invalid:
            raise Exception('No valid course selected')

        # Get execution time start
        self.ExecutionTime_Start = time.time()
        # Wait until execution time is reached
        self.wait_until_time_is_reached()

        # Start browser
        self.start_browser()

        # Create list with all courses
        randList = [CourseType.Blue.value, CourseType.Red.value, CourseType.Yellow.value]
        # Remove fix selected onces
        for i in range(0,2):
            if lib.settings.Document['round'][i]['course_enum'].value in randList:
                print('Course {0} is set fix. Remove from random list'.format(lib.settings.Document['round'][i]['course_enum'].name))
                randList.remove(lib.settings.Document['round'][i]['course_enum'].value)

        print('')
        print('Init done...')
        print('')

        # Round 1
        round1TimeslotSelected, round1, randList = self.try_get_timeslot_round(_id=0, _randomCourseList= randList)

        # Round 2
        round2TimeslotSelected, round2, randList = self.try_get_timeslot_round(_id=1, _randomCourseList= randList)

        # Check if we could find all
        if not round1TimeslotSelected or not round2TimeslotSelected:
            print('Failed to book. No free slots found')
            return

        print(round1.Str_text)
        print(round1.Course.name)
        print(round2.Str_text)
        print(round2.Course.name)

    def wait_until_time_is_reached(self):
        print('Wait for execution date and time...')
        while lib.settings.Document['executiontime_converted'] > datetime.now():
            # Wait some time
            time.sleep(1)
        print('Time reached at', datetime.now())

    def start_browser(self):
        print('Start browser...')
        self.Browser = lib.CBrowser(lib.BrowserType.Chrome, lib.settings)
        self.Browser.login()
        self.Browser.booktimes()
        self.Browser.set_date()

    def close_browser(self):
        print('Close browser...')
        self.Browser.dispose()

    def try_get_timeslot_round(self, _id, _randomCourseList):
        round = None
        roundTimeslotSelected = False
        randomCourseList = _randomCourseList.copy()
        localCourseList = _randomCourseList.copy()
        if lib.settings.Document['round'][_id]['course_enum'] != CourseType.Invalid:
            if lib.settings.Document['round'][_id]['course_enum'] == CourseType.Any:
                done = False
                while not done:
                    # Get random course
                    randIndex = random.randint(0, len(localCourseList) - 1)
                    randCourse = localCourseList[randIndex]
                    localCourseList.remove(randCourse)

                    print('Random course selected {0}. Try get timeslot...'.format(CourseType(randCourse).name))

                    # Try get timeslot in this round
                    round = self.get_course_timeslot(_course=CourseType(randCourse), _timeSlotStart=lib.settings.Document['round'][_id]['timeslot_timespan_start'], _timeSlotEnd=lib.settings.Document['round'][_id]['timeslot_timespan_end'])
                    # Did we found something?
                    if round is not None:
                        randomCourseList.remove(randCourse)
                        roundTimeslotSelected = True
                        done = True
                        print('Random course available')
                        break
                    else:
                        # We found nothing remove current course from local list and try again
                        print('Random course NOT available')
                        if len(localCourseList) == 0:
                            done = True
                            print('No more random courses available... Booking failed')
                            break
            else:
                print('Fix course selected {0}. Try get timeslot...'.format(lib.settings.Document['round'][_id]['course_enum'].name))
                round = self.get_course_timeslot(_course=lib.settings.Document['round'][_id]['course_enum'], _timeSlotStart=lib.settings.Document['round'][_id]['timeslot_timespan_start'], _timeSlotEnd=lib.settings.Document['round'][_id]['timeslot_timespan_end'])
                if round is not None:
                    print('Fix course available')
                    roundTimeslotSelected = True
                else:
                    print('Fix course NOT available... Booking failed')
        else:
            print('No course selected for index {0}'.format(_id))
            roundTimeslotSelected = True

        return roundTimeslotSelected, round, randomCourseList

    def get_course_timeslot(self, _course, _timeSlotStart, _timeSlotEnd):

        self.Browser.set_course(_course=_course.name)

        # Parse timetable if not done yet
        timslots = dict()
        if _course == CourseType.Blue:
            if len(self.Timeslots_blue) == 0:
                self.Timeslots_blue = self.Browser.parse_timeslots(CourseType.Blue)
            timeslots = self.Timeslots_blue
        elif _course == CourseType.Red:
            if len(self.Timeslots_red) == 0:
                self.Timeslots_red = self.Browser.parse_timeslots(CourseType.Red)
            timeslots = self.Timeslots_red
        elif _course == CourseType.Yellow:
            if len(self.Timeslots_yellow) == 0:
                self.Timeslots_yellow = self.Browser.parse_timeslots(CourseType.Yellow)
            timeslots = self.Timeslots_yellow

        # Check if we find free time slot on course
        for key in timeslots:
            # At first timeslot needs to be free
            if timeslots[key].IsFree:
                # Check if time is in range
                if timeslots[key].Slot >= _timeSlotStart and timeslots[key].Slot <= _timeSlotEnd:
                    return timeslots[key]

        return None

main = ExecutionController()
main.run()


'''
print('Start browser...')
browser_blue = lib.CBrowser(lib.BrowserType.Chrome, lib.settings)
browser_blue.login()

browser_red = lib.CBrowser(lib.BrowserType.Chrome, lib.settings)
browser_red.login()

browser_yellow = lib.CBrowser(lib.BrowserType.Chrome, lib.settings)
browser_yellow.login()

# Go to booking times and set date & course
browser_blue.booktimes()
browser_blue.set_date(_id=i)
browser_blue.set_course(_id=i)
# Parse all times
browser_blue.parse_timeslots()

# Do reservation if found
#browser.reservation(_id=i)
#browser.partner_reservation(_id=i)
#browser.send_reservation()
#browser.move_default()

#browser.logout()
#browser.dispose()

timeend = time.time()
print('Execution time', timeend - timestart)
'''