# SHLiC

## Overview
SHLiC (Simple Holiday Lighting Controller) is a home brew device for controlling outside (or really inside as well) outlets for simple lighting control.  "Simple" meaning, outlet on/off.  It is controllable through an HTTP REST interface.

The need came from my frustration of using X10 and WiFi enabled outlets to control my holiday lighting, with mixed successes.  As such, all of the features are based on my needs & requests to myself, based on my holiday lighting needs.  My goal was to have something controllable via any service or device that talks REST (ie, OpenHab)

## Features
SHLiC may be Simple, but that doesn't mean it's not robust. 

## Prerequisites
SHLiC requires the following software to work
* Python 2.7
* virtualenv (pip install virtualenv)
* Flask (Python Library) (pip install flask)
* gpiozero (pip install gpiozero)
* pymemcache (pip install pymemcache)

## Principals of Operation
1. SHLiC should accept REST commands to control the status of a relay.
	* Should also support an "all on" and "all off" command
2. Local control (physical control of the output relays at the location) is required.
   * When local lockout is enabled, block all remote commands to the controller
   * When local lockout is disabled, return the state of the relays to the state they should be in based on remote commands that have happened since lockout started.

## Features to Add
* Server component for centralized control

## Manual installation instructions
1. Start with Python 2.7 installed (part of the base raspbian install)
2. sudo apt-get install python-pip
3. sudo pip install virtualenv
4. sudo adduser shlic
5. sudo su shlic
6. cd ~
7.  virtualenv -p /usr/bin/python shlic
8.  source shlic/bin/activate
9.  pip install flask
10. pip install gpiozero
11. pip install pymemcache
12. cd ~/shlic
13. copy the app files in here

to run:
gunicorn --bind 0.0.0.0:5000 runController:controller.engine.app

## Design Details
### Hardware Spec
#### Controller Part List
* Dry box ( HxWxH )
* Raspberry Pi 3 [Amazon](https://www.amazon.com/Raspberry-Pi-RASPBERRYPI3-MODB-1GB-Model-Motherboard/dp/B01CD5VC92) / Adafruit
* 8-Channel Relay Board [Amazon](https://www.amazon.com/gp/product/B00KTELP3I/ref=oh_aui_search_detailpage?ie=UTF8&psc=1)
* 4-Port High Output USB Charger [Amazon](https://www.amazon.com/gp/product/B00OT6YUIY/ref=oh_aui_detailpage_o00_s00?ie=UTF8&psc=1)
* Blue Sea Systems Common BusBar (100a, 5 Screw, w/ Cover) [Amazon](https://www.amazon.com/gp/product/B000OTJ89Q/ref=oh_aui_detailpage_o00_s00?ie=UTF8&psc=1)
* Blue Sea Systems DualBus 100 Amp Common Bus 2701 [Amazon](https://www.amazon.com/Blue-Sea-Systems-DualBus-BusBar/dp/B000K2K6M0/ref=sr_1_3?ie=UTF8) --or-- [Amazon](https://www.amazon.com/Blue-Sea-Systems-DualBus-BusBar/dp/B000K2MABA/ref=sr_1_2?ie=UTF8)
* 8x 1ft Extension Cords [Amazon](https://www.amazon.com/gp/product/B00CEJW0WQ/ref=oh_aui_detailpage_o00_s00?ie=UTF8&psc=1)
*
#### GPIO Assignments
##### Relays
* Relay 1: 5
* Relay 2: 6
* Relay 3: 12
* Relay 4: 13
* Relay 5: 16
* Relay 6: 19
* Relay 7: 20
* Relay 8: 21

##### Button Controls
* Local Lockout Switch: 4
* Local Control Switch: 18

##### LEDs
* Ready: 22
* Local Lockout Status: 17
* Local Control Status: 27

