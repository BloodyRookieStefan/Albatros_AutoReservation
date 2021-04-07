import lib
from datetime import datetime

print('Wait for execution date and time...')

# TODO: Wait for execution time
now = datetime.now()
current_time = now.strftime("%H:%M:%S")

# TODO: Hand over settings here
browser = lib.CBrowser(lib.BrowserType.Chrome)
for i in range(0, len(lib.settings.Document['round'])):
    # Check if we need login
    if i == 0:
        browser.login()
    browser.booktimes()
    browser.reservation(_id=i)
    browser.partner_reservation(_id=i)
    browser.send_reservation()

browser.logout()
browser.dispose()