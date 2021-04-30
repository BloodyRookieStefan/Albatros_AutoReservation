import lib
import time
import random
import itertools

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

        # Pre check if valid course is set
        if lib.settings.Document['round'][0]['course_enum'] == CourseType.Invalid and lib.settings.Document['round'][1]['course_enum'] == CourseType.Invalid:
            raise Exception('Both course types are invalid. No valid course selected')

        # Get execution time start
        self.ExecutionTime_Start = time.time()
        # Wait until execution time is reached
        self.wait_until_time_is_reached()

        # Start browser
        self.start_browser()

        print('')
        print('Init done...')
        print('')

        courseCombinations = self.get_all_possible_combinations()
        round1Set = False
        round2Set = False
        for combi in courseCombinations:
            # Check if all found
            if round1Set and round2Set:
                print('Combination valid')
                break

            print('Check combination Round 1: {0}, Round 2: {1}'.format(combi[0].name, combi[1].name))

            # Round 1
            if combi[0] != CourseType.Invalid:
                round1 = self.get_course_timeslot(_course=combi[0], _timeSlotStart=lib.settings.Document['round'][0]['timeslot_timespan_start'], _timeSlotEnd=lib.settings.Document['round'][0]['timeslot_timespan_end'])

                if round1 is not None:
                    round1Set = True
            else:
                round1Set = True

            # Round 2
            if combi[1] != CourseType.Invalid:
                if (lib.settings.Document['roundMINdelay_converted'].hour > 0 or lib.settings.Document['roundMINdelay_converted'].minute > 0 or \
                    lib.settings.Document['roundMAXdelay_converted'].hour > 0 or lib.settings.Document['roundMAXdelay_converted'].minute > 0) and \
                    round1 is not None:

                    timeslotStart = round1.Slot
                    timeslotEnd = round1.Slot

                    hour = timeslotStart.hour + lib.settings.Document['roundMINdelay_converted'].hour
                    minute = timeslotStart.minute + lib.settings.Document['roundMINdelay_converted'].minute
                    if minute > 59:
                        hour = hour + 1
                        minute = minute - 59
                    timeslotStart = datetime(timeslotStart.year, timeslotStart.month, timeslotStart.day, hour, minute, 0)

                    hour = timeslotEnd.hour + lib.settings.Document['roundMAXdelay_converted'].hour
                    minute = timeslotEnd.minute + lib.settings.Document['roundMAXdelay_converted'].minute
                    if minute > 59:
                        hour = hour + 1
                        minute = minute - 59
                    timeslotEnd = datetime(timeslotEnd.year, timeslotEnd.month, timeslotEnd.day, hour, minute, 0)

                    print('Delay option for course 2 - Delay time MIN {0} - Delay time MAX {1}'.format(timeslotStart.strftime('%H:%M'), timeslotEnd.strftime('%H:%M')))
                else:
                    timeslotStart = lib.settings.Document['round'][1]['timeslot_timespan_start']
                    timeslotEnd = lib.settings.Document['round'][1]['timeslot_timespan_end']

                    print('Choose normal start time for course 2')

                round2 = self.get_course_timeslot(_course=combi[1], _timeSlotStart=timeslotStart, _timeSlotEnd=timeslotEnd)

                if round2 is not None:
                    round2Set = True
            else:
                round2Set = True

        if not round1Set or not round2Set:
            print('FAILED: Could not find valid time slot')
            return

        if round1 is not None:
            print('Round 1 selected => Timeslot: {0}, Course: {1}, IsFree: {2} '.format(round1.Slot.strftime('%d.%m.%Y - %H:%M'), round1.Course.name, round1.IsFree))
        else:
            print('Round 1 => None')
        if round2 is not None:
            print('Round 2 selected => Timeslot: {0}, Course: {1}, IsFree: {2} '.format(round2.Slot.strftime('%d.%m.%Y - %H:%M'), round2.Course.name, round2.IsFree))
        else:
            print('Round 2 => None')

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

    def  get_all_possible_combinations(self):

        combinations = list()
        combinations_sorted = list()
        round1List = list()
        round2List = list()

        if lib.settings.Document['round'][0]['course_enum'] != CourseType.Invalid:
            if lib.settings.Document['round'][0]['course_enum'] == CourseType.Any:
                round1List = [CourseType.Blue.value, CourseType.Red.value, CourseType.Yellow.value]
            else:
                round1List = [lib.settings.Document['round'][0]['course_enum'].value]
        else:
            if lib.settings.Document['round'][1]['course_enum'] == CourseType.Any:
                combinations_sorted.append((CourseType.Invalid, CourseType.Blue))
                combinations_sorted.append((CourseType.Invalid, CourseType.Red))
                combinations_sorted.append((CourseType.Invalid, CourseType.Yellow))
            else:
                combinations_sorted.append((CourseType.Invalid, lib.settings.Document['round'][1]['course_enum']))
            # Shuffle list
            random.shuffle(combinations_sorted)
            return combinations_sorted

        if lib.settings.Document['round'][1]['course_enum'] != CourseType.Invalid:
            if lib.settings.Document['round'][1]['course_enum'] == CourseType.Any:
                round2List = [CourseType.Blue.value, CourseType.Red.value, CourseType.Yellow.value]
            else:
                round2List = [lib.settings.Document['round'][1]['course_enum'].value]
        else:
            if lib.settings.Document['round'][0]['course_enum'] == CourseType.Any:
                combinations_sorted.append((CourseType.Blue, CourseType.Invalid))
                combinations_sorted.append((CourseType.Red, CourseType.Invalid))
                combinations_sorted.append((CourseType.Yellow, CourseType.Invalid))
            else:
                combinations_sorted.append((lib.settings.Document['round'][0]['course_enum'], CourseType.Invalid))
            # Shuffle list
            random.shuffle(combinations_sorted)
            return combinations_sorted

        # Build all combinations with itertools
        # Depending on list length get permutations
        if len(round1List) >= len(round2List):
            permutations = itertools.permutations(round1List, len(round2List))
            zipObject = round2List
        else:
            permutations = itertools.permutations(round2List, len(round1List))
            zipObject = round1List
        for permutation in permutations:
            zipped = zip(permutation, zipObject)
            combinations.append(list(zipped))

        # Build sorted list => Not interested in:
        # Same tuples (1,1) or (2,2) or (3,3)
        # Already known combinations [(3,1), (3,2), (2,1)] and [(3,1), (2,3), (1,2)] => e.g (3,1)
        for combination in combinations:
            for tuple in combination:
                if len(tuple) > 1 and tuple[0] != tuple[1]:
                    # Based on list length create tuple that round1 is always index 0
                    if len(round1List) >= len(round2List):
                        courseTuple = (CourseType(tuple[0]), CourseType(tuple[1]))
                    else:
                        courseTuple = (CourseType(tuple[1]), CourseType(tuple[0]))
                    if courseTuple not in combinations_sorted:
                        combinations_sorted.append(courseTuple)

        # Shuffle list
        random.shuffle(combinations_sorted)
        return combinations_sorted

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

if __name__ == "__main__":
    main = ExecutionController()
    main.run()