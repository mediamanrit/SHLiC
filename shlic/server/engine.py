"""
This is the engine for the server portion of SHLiC
"""
from flask import Flask
from flask import request
import gpiozero
from pymemcache.client.base import Client as memcache
import requests

app = Flask(__name__)
app.config.from_pyfile('../../shlic-server.cfg')

#Setup default configuration values, and define them if they config file doesn't
if app.config["DEBUG"]:
    configDebug = app.config["DEBUG"]
else:
    configDebug = False

if app.config["PORT"]:
    configPort = app.config["PORT"]
else:
    configPort = 5000

if app.config["KEY"]:
    configKey = app.config["KEY"]
else:
    configKey = "ThisIsTheDefaultKey-ChangeMe"

if app.config["CLIENTS"]:
    configClients = app.config["CLIENTS"]
else:
    configClients = ""

if configDebug:
    print "CLIENTS - %s" % configClients

if app.config["CLIENTKEY"]:
    configClientKey = app.config["CLIENTKEY"]
else:
    configClientKey = "ThisIsTheDefaultKey-ChangeMe"

#Parse the configClients
clientAddresses = configClients.split(",")
if configDebug:
    for oneClient in clientAddresses:
        print "oneClient - %s" % oneClient

#Setup memcache
cache = memcache(('localhost',11211))

#Buttons & Switches
manualSwitch = gpiozero.Button(24)
scheduleEnableSwitch = gpiozero.Button(14)
#switch2 = gpiozero.Button(15)
#switch3 = gpiozero.Button(18)
#switch4 = gpiozero.Button(23)
resendStateButton = gpiozero.Button(3)
#button2 = gpiozero.Button(2)

#LEDs
stateLED = gpiozero.LED(19)
state2LED = gpiozero.LED(26)

#Function to control all slave controllers
def controlAll(state):
    if state == "on":
        for oneClient in clientAddresses:
            postParams = {'key':configClientKey}
            url = "http://%s/api/relayControl/on" % oneClient
            print "sending \"on\" to %s " % url
            try:
                r = requests.post(url,data=postParams)
            except:
                print "ERROR: Cannot connect to %s" % url
                pass
            cache.set("allControllerState","1")
        return "ON"
    elif state == "off":
        for oneClient in clientAddresses:
            postParams = {'key':configClientKey}
            url = "http://%s/api/relayControl/off" % oneClient
            print "sending \"off\" to %s " % url
            try:
                r = requests.post(url,data=postParams)
            except:
                print "ERROR: Cannot connect to %s" % url
                pass
            cache.set("allControllerState","0")
        return "OFF"
    else:
        return False

def disableSchedule():
    cache.set("scheduleEnabled","0")

def enableSchedule():
    cache.set("scheduleEnabled","1")

def disableManual():
    cache.set("manualEnabled","0")
    controlAll("off")

def enableManual():
    cache.set("manualEnabled","1")
    controlAll("on")

def resendState():
    currentState = cache.get("allControllerState")
    if currentState == "1":
        print "Resending \"on\" to all"
        controlAll("on")
    elif currentState == "0":
        print "Resending \"on\" to all"
        controlAll("off")
    else:
        return False

#Startup local control switch state check
if scheduleEnableSwitch.is_pressed:
    enableSchedule()
else:
    disableSchedule()

if manualSwitch.is_pressed:
    enableManual()
else:
    disableManual()

scheduleEnableSwitch.when_pressed = enableSchedule
scheduleEnableSwitch.when_released = disableSchedule
manualSwitch.when_pressed = enableManual
manualSwitch.when_released = disableManual
resendStateButton.when_pressed = resendState

def authenticateUser(password):
	if (password == configKey):
		return True
	else:
		return False

#REST page to check the status of the service (aka ping)
@app.route("/api/ping", methods=['POST', 'GET'])
def ping():
    if request.method == 'POST':
        if not authenticateUser(request.form['key']):
            return "no auth"
    return "PONG - GET w/o Auth"

#REST page to get the status
@app.route("/api/getStatus", methods=['GET', 'POST'])
def getStatusPage():
    if not authenticateUser(request.form['key']):
        return "ERROR: no authentication"
    output = "Hi!"
    return output

#REST page to run scheduled start
@app.route("/api/schedule/<state>", methods=['GET', 'POST'])
def schedulePage(state):
    if not authenticateUser(request.form['key']):
        return "ERROR: no authentication"
    if state == "on":
        controlAll("on")
        output = "OK"
    elif state == "off":
        controlAll("off")
        output = "OK"
    else:
        output = "ERROR: bad state request"
    return output
