'''
#############################################################################################
@brief Main file to control webpage
@param Pipe - Python PIPE for communication
@param BackendBooted - Flag if backend is booted
@param ReadTimeoutInSec - Time within we expect an response from backend
@param TemplateDocument - Read template dict
#############################################################################################
'''

from flask import Flask, render_template, request, redirect, url_for
from GlobalLib.template_control import CTemplateCreator
from datetime import datetime, timedelta
from GlobalLib.pipe import CPipe, PipeOperation

import logging

# Com pipe
Pipe = None
# General
BackendBooted = False
ReadTimeoutInSec = 1
# Web app
app = Flask(__name__)
# Set logger only to error
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

TemplateDocument = CTemplateCreator().read_template()

def thread_init(conn):
    print('Startup Frontend - Params: developmode={0}, fastbootmode={1}, debugmessages={2}...'.format(TemplateDocument['developermode'], TemplateDocument['fastbootmode'], TemplateDocument['debugmessages']))

    global Pipe, BackendBooted
    Pipe = CPipe(conn, TemplateDocument['debugmessages'])
    BackendBooted = False
    app.run()
    #app.run('192.168.59.100')

def get_formated_date(date):
    # Day
    dateD = str(date.day)
    if date.day < 10:
        dateD = "0" +str(date.day)
    # Month
    dateM = str(date.month)
    if date.month < 10:
        dateM = "0" +str(date.month)
    # Year
    dateY = str(date.year)

    return dateD, dateM, dateY

@app.route("/")
def index():
    global BackendBooted
    # Check if backend has booted
    if not BackendBooted:
        operation, data = Pipe.get_data(timeout=ReadTimeoutInSec)
        if operation == PipeOperation.InvalidOperation:
            return redirect(url_for("failed", errordata='Backend not booted yet. Please try again in a couple of minutes...'))
        elif operation == PipeOperation.BackendBooted:
            BackendBooted = True

    # Get data => Send course layout request
    courseLayout = pipe_handler(commandSend=PipeOperation.Req_CourseLayout, expectedResp=PipeOperation.Resp_CourseLayout)
    # Get data => Send course status request
    courseStatus = pipe_handler(commandSend=PipeOperation.Req_CourseStatus, expectedResp=PipeOperation.Resp_CourseStatus)
    # Get data => Send course booking in progress
    bookingInProgess = pipe_handler(commandSend=PipeOperation.Req_ReqInProgress, expectedResp=PipeOperation.Resp_ReqInProgress)

    if courseLayout is None or courseStatus is None or bookingInProgess is None:
        return redirect(url_for("failed", errordata='Backend seems to be busy. Please try again in a couple of minutes...'))

    # Check if course layout is available
    courseLayoutPresent = True
    if len(courseLayout) == 0:
        courseLayoutPresent = False

    courseStatusPresent = True
    if len(courseStatus) == 0:
        courseStatusPresent = False

    # Get current date, month and year
    currentDateD, currentDateM, currentDateY = get_formated_date(datetime.now())
    # Get last update date, month and year
    lastCourseUpdateD, lastCourseUpdateM, lastCourseUpdateY = get_formated_date(courseStatus['timestamp'] if courseStatusPresent else datetime.min)

    return render_template("index.html", bookdateD=(datetime.now() + timedelta(days=TemplateDocument['executespan'])).day, bookdateM=(datetime.now() + timedelta(days=TemplateDocument['executespan'])).month, bookdateY=(datetime.now() + timedelta(days=TemplateDocument['executespan'])).year,
                           currentDateD=currentDateD,
                           currentDateM=currentDateM,
                           currentDateY=currentDateY,
                           username=TemplateDocument['username'],
                           bookinginprogess=bookingInProgess,
                           courseLayoutPresent=courseLayoutPresent,
                           courseLayout=courseLayout,
                           courseStatusPresent=courseStatusPresent,
                           courseStatus=courseStatus,
                           lastCourseUpdateD=lastCourseUpdateD,
                           lastCourseUpdateM=lastCourseUpdateM,
                           lastCourseUpdateY=lastCourseUpdateY)

@app.route("/success")
def success():
    return render_template("response.html", errordata=None, button='success')

@app.route("/cancel", methods=['POST'])
def cancel():
    # Send new cancel request
    Pipe.send_data(PipeOperation.Req_CancelReq)
    operation, data = Pipe.get_data(timeout=ReadTimeoutInSec)
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

    # Replace data
    TemplateDocument['date'] = date
    TemplateDocument['courseBooking'] = int(layout)
    round = TemplateDocument['round'][0]
    round['start_timeslot'] = timespanStart
    round['end_timeslot'] = timespanEnd
    if useWeatherData is not None:
        TemplateDocument['use_nice_weather_golfer'] = 1
        TemplateDocument['minTemp_deg'] = int(minTemp)
        TemplateDocument['maxRainChange_perc'] = int(maxRain)
        TemplateDocument['maxWind_km/h'] = int(maxWind)
    else:
        TemplateDocument['use_nice_weather_golfer'] = 0

    for i in range(0, 3):
        if partnerList[i][0] != '' and partnerList[i][1] != '':
            partner = round['partner{}'.format(i)][0]
            partner['firstName'] = partnerList[i][1]
            partner['lastName'] = partnerList[i][0]

    # Send new request
    pipe_handler(commandSend=PipeOperation.Req_NewReq, expectedResp=PipeOperation.Resp_NewReq, data=TemplateDocument)

    return redirect(url_for("success"))
# ----------------------------------------------------------------------------------------
def pipe_handler(commandSend, expectedResp, data=dict()):
    # Send command
    Pipe.send_data(commandSend, data)
    # Wait for response
    operation, data = Pipe.get_data(timeout=ReadTimeoutInSec)

    if operation != expectedResp:
        return None
    return data


