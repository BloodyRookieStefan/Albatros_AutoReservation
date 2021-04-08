import lib
import time
from datetime import datetime

print('Wait for execution date and time...')

# TODO: Wait for execution time
now = datetime.now()
current_time = now.strftime("%H:%M:%S")

browser = lib.CBrowser(lib.BrowserType.Chrome, lib.settings)
browser.login()

for i in range(0, len(lib.settings.Document['round'])):

    # Go to booking times and set date & course
    browser.booktimes()
    browser.set_date(_id=i)
    browser.set_course(_id=i)

    # Get if reservation is enabled yet
    resAvailable = False
    for i in range(0, 12):
        if browser.res_timeslots_available(_id=id):
            resAvailable = True
            break
        else:
            # Wait 10 seconds and refresh browser
            time.sleep(10)
            browser.refresh()

    # Do reservation if found
    if resAvailable:
        browser.reservation(_id=i)
        browser.partner_reservation(_id=i)
        browser.send_reservation()
    else:
        pass

browser.logout()
browser.dispose()