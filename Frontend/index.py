import os
import re

from flask import Flask, render_template, request, redirect, url_for
from template_creator import CTemplateCreator
from datetime import datetime, timedelta

app = Flask(__name__)
tempCreator = CTemplateCreator()
tempCreator.read_template()

@app.route("/")
def index():
    # Check if booking is in progress
    bookingInProgess = False
    if os.path.exists(tempCreator.TargetFile):
        bookingInProgess = True
    # Check if course layout is available
    courseLayoutPresent = True
    courseLayout = get_course_layout()
    if len(courseLayout) == 0:
        courseLayoutPresent = False

    return render_template("index.html", currentdateD=(datetime.now() + timedelta(days=3)).day, currentdateM=(datetime.now() + timedelta(days=3)).month, currentdateY=(datetime.now() + timedelta(days=3)).year,
                           username=tempCreator.Document['username'],
                           bookinginprogess=bookingInProgess,
                           courseLayoutPresent=courseLayoutPresent,
                           courseLayout=courseLayout)

@app.route("/success")
def success():
    return render_template("response.html", errordata=None, cancel=False)

@app.route("/cancel", methods=['POST'])
def cancel():
    if os.path.exists(tempCreator.TargetFile):
        os.remove(tempCreator.TargetFile)
    return render_template("response.html", errordata=None, cancel=True)

@app.route("/failed/<errordata>")
def failed(errordata):
    return render_template("response.html", errordata=errordata, cancel=False)

@app.route("/home", methods=['POST'])
def home():
    return redirect(url_for("index"))

@app.route('/response', methods=['POST'])
def response():
    # Get data from website
    layout = request.form.get("courseLayout")
    date = '{}.{}.{}'.format(request.form.get("dateD"), request.form.get("dateM"), request.form.get("dateY"))
    timespanStart = '{}-{}'.format(request.form.get("startH"), request.form.get("startM"))
    timespanEnd = '{}-{}'.format(request.form.get("endH"), request.form.get("endM"))
    useWeatherData = request.form.get("useWeatherData")
    minTemp = request.form.get("minTemp")
    maxRain = request.form.get("maxRain")
    maxWind = request.form.get("maxWind")
    partnerList = []
    for i in range(1, 4):
        firstName = request.form.get("firstName{0}".format(i))
        lastName = request.form.get("lastName{0}".format(i))

        partnerList.append((lastName, firstName))

    # Validate input data
    if useWeatherData is not None:
        if not check_input(_type='DIGITONLY', _value=minTemp):
            return redirect(url_for("failed", errordata=format_error_str("MINIMUM TEMPERATURE", "digit only", minTemp)))
        if not check_input(_type='DIGITONLY', _value=maxRain):
            return redirect(url_for("failed", errordata=format_error_str("MAXIMUM RAIN CHANCE", "digit only", maxRain)))
        if not check_input(_type='DIGITONLY', _value=maxWind):
            return redirect(url_for("failed", errordata=format_error_str("MAXIMUM WIND SPEED", "digit only", maxWind)))

    # Replace data
    tempCreator.Document['date'] = date
    tempCreator.Document['courseBooking'] = int(layout)
    round = tempCreator.Document['round'][0]
    round['start_timeslot'] = timespanStart
    round['end_timeslot'] = timespanEnd
    if useWeatherData is not None:
        tempCreator.Document['use_nice_weather_golfer'] = 1
        tempCreator.Document['minTemp_deg'] = int(minTemp)
        tempCreator.Document['maxRainChange_perc'] = int(maxRain)
        tempCreator.Document['maxWind_km/h'] = int(maxWind)
    else:
        tempCreator.Document['use_nice_weather_golfer'] = 0

    for i in range(0, 3):
        if partnerList[i][0] != '' and partnerList[i][1] != '':
            partner = round['partner{}'.format(i)][0]
            partner['firstName'] = partnerList[i][1]
            partner['lastName'] = partnerList[i][0]

    tempCreator.save_template()

    return redirect(url_for("success"))

def check_input(_type, _value):
    if _type == 'DATE':
        if re.search('^[0-9]{1,2}\.[0-9]{1,2}\.[0-9]{4}$', _value):
            dateSplit = _value.split('.')
            if int(dateSplit[0]) < 1 or int(dateSplit[0]) > 31:
                print(1)
                return False
            if int(dateSplit[1]) < 1 or int(dateSplit[1]) > 12:
                print(2)
                return False
            if int(dateSplit[2]) < datetime.now().year:
                print(3)
                return False
            return True
        else:
            return False
    elif _type == 'TIMEVALUE':
        timeSplit = _value.split('.')
        if re.search('^[0-9]{1,2}-[0-9]{1,2}$', _value):
            return True
        else:
            return False
    elif _type == 'DIGITONLY':
        if re.search('^[0-9]+$', _value):
            return True
        else:
            return False

def format_error_str(_item, _expected, _got):
    return "{0} had not the correct format - Expected: \"{1}\" - Got: \"{2}\"".format(_item, _expected, _got)

def get_course_layout():
    return tempCreator.read_course_layout()

if __name__ == "__main__":
    app.run()
    #app.run("192.168.59.100")
