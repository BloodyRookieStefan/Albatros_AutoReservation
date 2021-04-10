import lib
import time
from datetime import datetime

timestart = time.time()

# Print out all settings
print('--------')
print('Execution at', lib.settings.Document['executiontime_converted'].strftime("%d:%m:%Y"), lib.settings.Document['executiontime_converted'].strftime("%H:%M:%S"))
for i in range(0, len(lib.settings.Document['round'])):
    print('Round', lib.settings.Document['round'][i]['course'], lib.settings.Document['round'][i]['timeslot_converted'].strftime("%d:%m:%Y"), lib.settings.Document['round'][i]['timeslot_converted'].strftime("%H:%M:%S"))
print('Workspace', lib.settings.Document['workspace'])
print('--------')

print('Wait for execution date and time...')

# TODO: Wait for execution time
now = datetime.now()
current_time = now.strftime("%H:%M:%S")

print('Start browser...')
browser = lib.CBrowser(lib.BrowserType.Chrome, lib.settings)
browser.login()

# Check if all times are available before booking
timesavalible = True
for i in range(0, len(lib.settings.Document['round'])):
    # Go to booking times and set date & course
    browser.booktimes()
    browser.set_date(_id=i)
    browser.set_course(_id=i)
    timesavalible = browser.check_timeslot(_id=i)
    browser.move_default()

    # Stop if one time is not available
    if not timesavalible:
        print('At least one timeslot is blocked. Cancel booking')
        break

if timesavalible:
    for i in range(0, len(lib.settings.Document['round'])):

        # Go to booking times and set date & course
        browser.booktimes()
        browser.set_date(_id=i)
        browser.set_course(_id=i)

        print('Check if times are available...')
        # Get if reservation is enabled yet
        resAvailable = False
        for j in range(0, 12):
            if browser.res_timeslots_available(_id=i):
                print('Booking times are available...')
                resAvailable = True
                break
            else:
                wait = 10
                print('No booking times avalable. Wait {} seconds and refresh...'.format(wait))
                # Wait 10 seconds and refresh browser
                time.sleep(wait)
                browser.refresh()

        # Do reservation if found
        if resAvailable:
            browser.reservation(_id=i)
            browser.partner_reservation(_id=i)
            browser.send_reservation()
        else:
            print('No booking times found...')
        browser.move_default()

browser.logout()
browser.dispose()

timeend = time.time()
print('Execution time', timeend - timestart)