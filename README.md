# Albatros AutoReservation
## Description

## Requirements
* Python 3.7 [www.python.org](https://www.python.org/)
* Get Selenium package => Open CMD Type `pip install -U selenium`
## Setup file
```yaml
username      : 
password      : 
roundMINdelay   : 02-00
roundMAXdelay   : 02-30
round         :
  - course    : Red
    start_timeslot: 11-00
    end_timeslot  : 12-00
    partner0  :
      - firstName : None
        lastName  : None
    partner1  :
      - firstName : None
        lastName  : None
    partner2:
      - firstName : None
        lastName  : None
    partner3  :
      - firstName : None
        lastName  : None
  - course    : Blue
    start_timeslot: 11-00
    end_timeslot  : 11-00
    partner0  :
      - firstName : None
        lastName  : None
    partner1  :
      - firstName : None
        lastName  : None
    partner2:
      - firstName : None
        lastName  : None
    partner3  :
      - firstName : None
        lastName  : None
date            : 02.05.2021
executedate     : 10.04.2021
executetime     : 15-17-00
workspace       : Windows
weburl          : https://albatros.gc-sl.de/albport/
developermode   : False
```
`username` Your Albatros user name  
`password` Your Albatros user password

`roundMINdelay` When set >0 the second course start time will be delayed by minimum X hour/minutes  
`roundMAXdelay` When set >0 the second course start time will be delayed by maximum X hour/minutes  
Note: When   `roundXdelay` is set the start timespan of the second course will be ignored

`course` Valid course types are **None**, **Blue**, **Red**, **Yellow** and **Any**  
`start_timeslot` Timespan start for course  
`end_timeslot` Timespan end for course  
`firstName` Your partner first name  
`lastName` Your parnter last name

`date` Date on of play

`executedate` Execution date on that the booking should start  
`executetime` Execution time (h) on that the booking should start

`workspace` Where is it executed? **Windows** or **Linux**  
`weburl` Albatros URL  
`developermode` If **true** booking will not be send
## How to run
Execute `main.py`