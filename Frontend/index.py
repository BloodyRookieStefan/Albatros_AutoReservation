import os
import re

from flask import Flask, render_template, request, redirect, url_for
from .template_creator import CTemplateCreator
from datetime import datetime, timedelta
from GlobalLib.pipe import CPipe, PipeOperation

Pipe = None

app = Flask(__name__)

tempCreator = CTemplateCreator()
tempCreator.read_template()

backendBooted = False
readTimeoutInSec = 1

def thread_init(conn):
    print('Frontend init...')
    global Pipe, backendBooted
    Pipe = CPipe(conn)
    backendBooted = False
    app.run()
    #app.run('192.168.59.100')

@app.route("/")
def index():
    global backendBooted
    # Check if backend has booted
    if not backendBooted:
        operation, backendBooted = Pipe.get_data(timeout=readTimeoutInSec)
        if operation == PipeOperation.InvalidOperation:
            return redirect(url_for("failed", errordata='Backend not booted yet. Please try again in a couple of minutes...'))
        elif operation == PipeOperation.BackendBooted:
            backendBooted = True

    # Get data => Send course layout request
    Pipe.send_data(PipeOperation.Req_CourseLayout)
    operation, courseLayout = Pipe.get_data(timeout=readTimeoutInSec)
    # Get data => Send course status request
    Pipe.send_data(PipeOperation.Req_CourseStatus)
    operation, courseStatus = Pipe.get_data(timeout=readTimeoutInSec)
    # Get data => Send course booking in progress
    Pipe.send_data(PipeOperation.Req_ReqInProgress)
    operation, bookingInProgess = Pipe.get_data(timeout=readTimeoutInSec)


    # Check if course layout is available
    courseLayoutPresent = True
    if len(courseLayout) == 0:
        courseLayoutPresent = False

    courseStatusPresent = True
    if len(courseStatus) == 0:
        courseStatusPresent = False

    return render_template("index.html", currentdateD=(datetime.now() + timedelta(days=3)).day, currentdateM=(datetime.now() + timedelta(days=3)).month, currentdateY=(datetime.now() + timedelta(days=3)).year,
                           username=tempCreator.Document['username'],
                           bookinginprogess=bookingInProgess,
                           courseLayoutPresent=courseLayoutPresent,
                           courseLayout=courseLayout,
                           courseStatusPresent=courseStatusPresent,
                           courseStatus=courseStatus)

@app.route("/success")
def success():
    return render_template("response.html", errordata=None, button='success')

@app.route("/cancel", methods=['POST'])
def cancel():
    # Send new cancel request
    Pipe.send_data(PipeOperation.Req_CancelReq)
    operation, data = Pipe.get_data(timeout=readTimeoutInSec)
    return render_template("response.html", errordata=None, button='cancel')

@app.route("/failed/<errordata>")
def failed(errordata):
    return render_template("response.html", errordata=errordata, button='None')

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

    # Send new request
    Pipe.send_data(PipeOperation.Req_NewReq, tempCreator.Document)
    operation, data = Pipe.get_data(timeout=readTimeoutInSec)

    return redirect(url_for("success"))

def check_input(_type, _value):
    if _type == 'DIGITONLY':
        if re.search('^[0-9]+$', _value):
            return True
        else:
            return False
    else:
        raise Exception('Unkown check type', _type)

def format_error_str(_item, _expected, _got):
    return "{0} had not the correct format - Expected: \"{1}\" - Got: \"{2}\"".format(_item, _expected, _got)


