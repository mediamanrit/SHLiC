"""
This is the engine for the controller/client portion of SHLiC.
This runs on the remote boxes with the outlets that need to be controlled.
"""

from flask import Flask
from flask import request
import gpiozero
from pymemcache.client.base import Client as memcache

app = Flask(__name__)
app.config.from_pyfile('../../shlic-controller.cfg')

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

#Setup memcache
cache = memcache(('localhost',11211))

#Buttons & Switches
localLockoutSwitch = gpiozero.Button(4)
localControlSwitch = gpiozero.Button(18)

#LEDs
readyLED = gpiozero.LED(22)
localLockoutLED = gpiozero.LED(17)
localControlLED = gpiozero.LED(27)

#Relay drivers
relayObjects = {}
relayObjects[1] = gpiozero.OutputDevice(5)
relayObjects[2] = gpiozero.OutputDevice(6)
relayObjects[3] = gpiozero.OutputDevice(12)
relayObjects[4] = gpiozero.OutputDevice(13)
relayObjects[5] = gpiozero.OutputDevice(16)
relayObjects[6] = gpiozero.OutputDevice(19)
relayObjects[7] = gpiozero.OutputDevice(20)
relayObjects[8] = gpiozero.OutputDevice(21)

cache.set("localLockoutState","0")
cache.set("localControlState","0")

#Functions

def authenticateUser(password):
	if (password == configKey):
		return True
	else:
		return False

def enableLocalLockout():
    cache.set("localLockoutState","1")
    localLockoutLED.on()

def disableLocalLockout():
    cache.set("localLockoutState","0")
    #Loop through the relays, setting their status to what it should be
    for onerelay in relayObjects:
        cachekey = "r%sstate" % onerelay
        cachedstate = cache.get(cachekey)
        if cachedstate == "on":
            relayObjects[onerelay].on()
        else:
            relayObjects[onerelay].off()
    localLockoutLED.off()

def allOnLocal():
    relayObjects[1].on()
    relayObjects[2].on()
    relayObjects[3].on()
    relayObjects[4].on()
    relayObjects[5].on()
    relayObjects[6].on()
    relayObjects[7].on()
    relayObjects[8].on()
    localControlLED.on()
    print "All On Locally"

def allOffLocal():
    relayObjects[1].off()
    relayObjects[2].off()
    relayObjects[3].off()
    relayObjects[4].off()
    relayObjects[5].off()
    relayObjects[6].off()
    relayObjects[7].off()
    relayObjects[8].off()
    localControlLED.off()
    print "All Off Locally"

#relayControl: Control relays
#  return values:
#  0: OK
#  1: Error
#  2: Queued
def relayControl(relay,state):
    if state == "on" :
        cachekey = "r%sstate" % relay
        cache.set(cachekey,"on")
        if cache.get("localLockoutState") != "1":
            relayObjects[relay].on()
            return 0
        else:
            return 2
    elif state == "off":
        cachekey = "r%sstate" % relay
        cache.set(cachekey,"off")
        if cache.get("localLockoutState") != "1":
            relayObjects[relay].off()
            return 0
        else:
            return 2
    else:
        return 1


#Startup local control switch state check
if localLockoutSwitch.is_pressed:
    enableLocalLockout()
else:
    disableLocalLockout()

if localControlSwitch.is_pressed:
    allOnLocal()
else:
    allOffLocal()

#Button Controls -> function mapping
localLockoutSwitch.when_pressed = enableLocalLockout
localLockoutSwitch.when_released = disableLocalLockout
localControlSwitch.when_pressed = allOnLocal
localControlSwitch.when_released = allOffLocal

#Startup
readyLED.on()

#REST Server Targets

@app.route("/")
def defaultpage():
    return "I'm awake!"

#REST page to check the status of the lockout state
@app.route("/api/ping", methods=['POST', 'GET'])
def ping():
    if request.method == 'POST':
        if not authenticateUser(request.form['key']):
            return "no auth"
    return "PONG - GET w/o Auth"

#REST page to check the status of the lockout state
@app.route("/api/getLockoutState", methods=['POST', 'GET'])
def getLockoutState():
    if not authenticateUser(request.form['key']):
        return "no auth"
    return "Local control lockout is: %s" % cache.get("localLockoutState")

#REST page to get the status of a relay
@app.route("/api/getRelayStatus/<relay>", methods=['GET', 'POST'])
def getRelayStatusPage(relay=0):
    if not authenticateUser(request.form['key']):
            return "no auth"
    relay = int(relay)
    if relay == 0:
        output = "Relay1: %s \n" %relayObjects[1].is_active
        output += "Relay2: %s \n" %relayObjects[2].is_active
        output += "Relay3: %s \n" %relayObjects[3].is_active
        output += "Relay4: %s \n" %relayObjects[4].is_active
        output += "Relay5: %s \n" %relayObjects[5].is_active
        output += "Relay6: %s \n" %relayObjects[6].is_active
        output += "Relay7: %s \n" %relayObjects[7].is_active
        output += "Relay8: %s \n" %relayObjects[8].is_active
    else:
        if relayObjects[relay].is_active:
            itis = "on"
        else:
            itis = "off"
        output = "Relay%s is %s \n" % (relay,itis)
        return output

#REST page to control the relays
@app.route("/api/relayControl/<state>/<relay>", methods=['GET', 'POST'])
@app.route("/api/relayControl/<state>", methods=['GET', 'POST'])
def relayControlPage(state,relay=0):
    if not authenticateUser(request.form['key']):
        return "no auth"
    relay = int(relay)
    if relay != 0 :
        controlResult = relayControl(relay,state)
        if controlResult == 0:
            return "OK: Relay %s turned %s" % (relay,state)
        elif controlResult == 1:
            return "Error:  Bad state request: %s" %state
        elif controlResult == 2:
            return "Warning: Local locout enabled.  Queueing change to relay %s" % relay
        else:
            return "Impossible error!!!"
    else:
        for onerelay in relayObjects:
            controlResult = relayControl(onerelay,state)
            if controlResult != "1":
                continue
            else:
                return "Error!  Bad state request: %s" %state
                break
        if cache.get("localLockoutState") == "1":
            return "Warning: Local locout enabled.  Queueing change to all relays"
        else:
            return "OK: All relays turned %s" % state
