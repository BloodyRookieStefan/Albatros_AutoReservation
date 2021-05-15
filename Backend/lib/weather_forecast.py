import copy

from datetime import datetime
from .basic_actions import CBasicActions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

class CWheaterForecast(CBasicActions):

    def __init__(self):
        pass

    def start_browser_wheater_forecast(self):
        # Load website
        self.Driver.get('https://www.agrarwetter.net')

        return self.parse_weather_forecast()

    def parse_weather_forecast(self):
        # Setup dict
        wheaterForecast = dict()

        # Set PLZ
        # Wait until present
        self.wait_until_tag_is_present(_type=By.ID, _tag="OrtodPlz")
        # Get element by ID
        element = self.Driver.find_element(By.ID, "OrtodPlz")
        element.send_keys("74382" +Keys.ENTER)

        # Number of move to next days
        for i in range(0, 3):

            # Wait until present
            self.wait_until_tag_is_present(_type=By.ID, _tag="DATUM")

            # Date
            tableEntriesDate = self.Driver.find_elements_by_xpath("//*[@id='DATUM']/td")

            # Temp
            tableEntriesTemp_0 = self.Driver.find_elements_by_xpath("//*[@id='T_0']/td")
            tableEntriesTemp_3 = self.Driver.find_elements_by_xpath("//*[@id='T_3']/td")
            tableEntriesTemp_6 = self.Driver.find_elements_by_xpath("//*[@id='T_6']/td")
            tableEntriesTemp_9 = self.Driver.find_elements_by_xpath("//*[@id='T_9']/td")
            tableEntriesTemp_12 = self.Driver.find_elements_by_xpath("//*[@id='T_12']/td")
            tableEntriesTemp_15 = self.Driver.find_elements_by_xpath("//*[@id='T_15']/td")
            tableEntriesTemp_18 = self.Driver.find_elements_by_xpath("//*[@id='T_18']/td")
            tableEntriesTemp_21 = self.Driver.find_elements_by_xpath("//*[@id='T_21']/td")

            # Wind
            tableEntriesWind_0 = self.Driver.find_elements_by_xpath("//*[@id='WGESCHW_0']/td")
            tableEntriesWind_3 = self.Driver.find_elements_by_xpath("//*[@id='WGESCHW_3']/td")
            tableEntriesWind_6 = self.Driver.find_elements_by_xpath("//*[@id='WGESCHW_6']/td")
            tableEntriesWind_9 = self.Driver.find_elements_by_xpath("//*[@id='WGESCHW_9']/td")
            tableEntriesWind_12 = self.Driver.find_elements_by_xpath("//*[@id='WGESCHW_12']/td")
            tableEntriesWind_15 = self.Driver.find_elements_by_xpath("//*[@id='WGESCHW_15']/td")
            tableEntriesWind_18 = self.Driver.find_elements_by_xpath("//*[@id='WGESCHW_18']/td")
            tableEntriesWind_21 = self.Driver.find_elements_by_xpath("//*[@id='WGESCHW_21']/td")

            # Chance of rain
            tableEntriesChanceOfRain_0 = self.Driver.find_elements_by_xpath("//*[@id='NW_0']/td")
            tableEntriesChanceOfRain_3 = self.Driver.find_elements_by_xpath("//*[@id='NW_3']/td")
            tableEntriesChanceOfRain_6 = self.Driver.find_elements_by_xpath("//*[@id='NW_6']/td")
            tableEntriesChanceOfRain_9 = self.Driver.find_elements_by_xpath("//*[@id='NW_9']/td")
            tableEntriesChanceOfRain_12 = self.Driver.find_elements_by_xpath("//*[@id='NW_12']/td")
            tableEntriesChanceOfRain_15 = self.Driver.find_elements_by_xpath("//*[@id='NW_15']/td")
            tableEntriesChanceOfRain_18 = self.Driver.find_elements_by_xpath("//*[@id='NW_18']/td")
            tableEntriesChanceOfRain_21 = self.Driver.find_elements_by_xpath("//*[@id='NW_21']/td")

            # Number of dates
            for j in range(0, 5):

                # Skip first
                if j == 0 or j > len(tableEntriesTemp_0) - 1:
                    continue

                debug = tableEntriesDate[j].text
                split = tableEntriesDate[j].text.split('\n')
                if len(split) == 2:
                    date = split[0]
                    day = split[1]

                tempList = []
                tempList.append(tableEntriesTemp_0[j].text)
                tempList.append(tableEntriesTemp_3[j].text)
                tempList.append(tableEntriesTemp_6[j].text)
                tempList.append(tableEntriesTemp_9[j].text)
                tempList.append(tableEntriesTemp_12[j].text)
                tempList.append(tableEntriesTemp_15[j].text)
                tempList.append(tableEntriesTemp_18[j].text)
                tempList.append(tableEntriesTemp_21[j].text)

                windList = []
                windList.append(tableEntriesWind_0[j].text)
                windList.append(tableEntriesWind_3[j].text)
                windList.append(tableEntriesWind_6[j].text)
                windList.append(tableEntriesWind_9[j].text)
                windList.append(tableEntriesWind_12[j].text)
                windList.append(tableEntriesWind_15[j].text)
                windList.append(tableEntriesWind_18[j].text)
                windList.append(tableEntriesWind_21[j].text)

                chanceOfRainList = []
                chanceOfRainList.append(tableEntriesChanceOfRain_0[j].text)
                chanceOfRainList.append(tableEntriesChanceOfRain_3[j].text)
                chanceOfRainList.append(tableEntriesChanceOfRain_6[j].text)
                chanceOfRainList.append(tableEntriesChanceOfRain_9[j].text)
                chanceOfRainList.append(tableEntriesChanceOfRain_12[j].text)
                chanceOfRainList.append(tableEntriesChanceOfRain_15[j].text)
                chanceOfRainList.append(tableEntriesChanceOfRain_18[j].text)
                chanceOfRainList.append(tableEntriesChanceOfRain_21[j].text)

                wheaterForecast[date] = CCast(_date=date, _day=day, _temp=tempList, _wind=windList, _chanceOfRain=chanceOfRainList)

            self.move_to_next_4_days()

        return wheaterForecast

    def move_to_next_4_days(self):
        # Wait until present
        self.wait_until_tag_is_present(_type=By.ID, _tag="ifa-angle-right")
        self.Driver.find_element(By.ID, "ifa-angle-right").click()


class CCast:

    Date = None                 # Date
    Day = None
    Temp = None                 # Temp in degree
    Wind = None                 # Wind in km/h
    ChanceOfRain = None         # Chance of rain in %

    def __init__(self, _date, _day, _temp, _wind, _chanceOfRain):

        dateSplit = _date.split('.')
        if len(dateSplit) == 3:
            self.Date = datetime(int(dateSplit[2]), int(dateSplit[1]), int(dateSplit[0]), 0, 0, 0)
        else:
            self.Date = None
        self.Day = _day

        # Init dict with timestamps
        self.Temp = dict()
        self.Wind = dict()
        self.ChanceOfRain = dict()
        i = 0
        j = 0
        # TODO: Interpolation?
        for time in range(0, 24):
            if i in [0, 3, 6, 9, 12, 15, 18, 21]:
                valueTemp = _temp[j].split(' ')[0]
                valueWind = _wind[j].split(' ')[0]
                valueRain = _chanceOfRain[j].split(' ')[0]
                j = j + 1
            self.Temp[time] = valueTemp
            self.Wind[time] = valueWind
            self.ChanceOfRain[time] = valueRain

            i = i + 1
