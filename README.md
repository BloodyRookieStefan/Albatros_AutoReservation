# Albatros AutoReservation
## Description
Auto booking for Albatrosservice Liebenstein [www.albatros.gc-sl.de/albport](https://albatros.gc-sl.de/albport/index.jsp?language=de&sid=7549441721F84A3CB517BA19E42010D6)
## Requirements
* Python 3.7 [www.python.org](https://www.python.org/)
* Selenium package
* Chrome webbrowser [www.google.de/chrome](https://www.google.de/chrome/?brand=CHBD&gclid=EAIaIQobChMI_8T96KrM8AIVCm8YCh3TGQYuEAAYASAAEgI32_D_BwE&gclsrc=aw.ds)
## How to install on Raspberry PI 4
* Install Ubuntu 20.04 LTS [www.ubuntu.com](https://ubuntu.com/download/raspberry-pi)
* Get latest updates: `sudo apt update && sudo apt upgrade -y`
* Install graphical overlay `sudo apt install Xfce`
* If not installed get Python3 `sudo apt-get install python3`
* Install pip command `sudo apt-get install python3-pip`
* Install Selenium `pip install selenium`
* Install Chrome webbrowser `sudo apt install chromium-browser`
* Install Chromium driver `sudo apt-get install chromium-chromedriver`
## Basic configuration
`/template.yaml`
```yaml
#---------------------------------------------
# Albatros login
username      : None                            # Albatros username
password      : None                            # Albatros password
#---------------------------------------------
# Booking
date            : None                          # Will be filled from template
courseBooking   : None                          # Will be filled from template
round:
  - start_timeslot: None                        # Will be filled from template
    end_timeslot  : None                        # Will be filled from template
    partner0:
      - firstName : None                        # Will be filled from template
        lastName  : None                        # Will be filled from template
    partner1:
      - firstName : None                        # Will be filled from template
        lastName  : None                        # Will be filled from template
    partner2:
      - firstName : None                        # Will be filled from template
        lastName  : None                        # Will be filled from template
    partner3:
      - firstName : None                        # Will be filled from template
        lastName  : None                        # Will be filled from template
#---------------------------------------------
# Weather data
use_nice_weather_golfer : None                  # Will be filled from template
minTemp_deg             : None                  # Will be filled from template
maxRainChange_perc      : None                  # Will be filled from template
maxWind_km/h            : None                  # Will be filled from template
#---------------------------------------------
# General settings
executespan       : 3                           # How many days before we can book in Albatros
executetime       : 21-00                       # Booking time
browser           : Chrome                      # Browser type. Currently Chrome only
weburl_booking    : https://albatros.gc-sl.de/albport/index.jsp?language=de&sid=7549441721F84A3CB517BA19E42010D6
# Develop
developermode     : 0                           # Dev mode
debugmessages     : 0                           # Print debug messages
fastbootmode      : 0                           # Only in combination with developermode = 1
```
`username` Your Albatros user name  
`password` Your Albatros user password

`executespan` How many day's in future you can book in Albatros  
`executetime` At which time is the next day activated  
`browser` Browser type  
`developermode` If **1** booking will not be send  
`fastbootmode` Backend boots faster and skips "course status", "course layout" check  
`weburl` Albatros URL

### Change IP adress for frontend
`Frontend/index.py`
```python
def thread_init(conn):
    print('Startup Frontend - Params: developmode={0}, fastbootmode={1}...'.format(TemplateDocument['developermode'], TemplateDocument['fastbootmode']))

    global Pipe, BackendBooted
    Pipe = CPipe(conn, TemplateDocument['developermode'])
    BackendBooted = False
    app.run()
    #app.run('192.168.59.100')
```
Following will run frontend on `127.0.0.1`
```python
app.run()
```
Following will run frontend on `192.168.59.100`
```python
app.run("192.168.59.100")
```

**Note**: Default port is 5000.  
You might need to open it on your Raspberry PI 4

## Configure auto login & start
### Set HDMI to active even if no monitor is detected
* Open your `/boot/boot.txt` on your Ubuntu installation (Hint: If you using an SD Card, plugg it in your PC card reader to access boot.txt)
* Add following lines to activate HDMI anytime:  
`hdmi_force_hotplug=1`  
`hdmi_drive=2`
* Reboot your Raspberry
### Auto login
1.) Open the Activities overview and start typing Users  
2.) Click Users to open the panel  
3.) Select the user account that you want to log in to automatically at startup  
4.) Press Unlock in the top right corner and type in your password when prompted  
5.) Switch the Automatic Login switch to on
### Auto start
Move to home directory `cd ~`  
Open your `.profile` file with `sudo nano .profile`  
At the end add following line:
```shell script
bash /home/<path to your Albatros folder>/bootAlbatrosService.sh
```
Navigate to your Albatros folder  
Open `bootAlbatrosService.sh` with `sudo nano bootAlbatrosService.sh`  
Change the path to your files
```shell script
#!/bin/sh
xterm -e python3 /home/ubuntu/AlbatrosReservation/main.py &
```
Make it executable with `sudo chmod 777 bootAlbatrosService.sh`  
After reboot frontend and backend should start automatically

## How to run manually
Execute `main.py`
