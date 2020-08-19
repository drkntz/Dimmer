# Dimmer.py
# This is a program which controls the firing of a triac from the GPIO pins of a raspberry Pi
# Created by Zach Martin on 28 Jul 2020
# 

import RPi.GPIO as GPIO
import time 
from Settings import *	# Settings file for this program. Notably, dimmerProfile defines which ramp up profile is used

GPIO.setmode(GPIO.BCM) # Uses the BCM pin definitions

##### Names for BCM GPIO pins
POWER = 14 	# Power LED
INC = 15 	# Increase delay
DEC = 18 	# Decrease delay
ZCROSS = 23	# Zero crossing input pin
TRIG = 24	# Triac trigger output pin

##### Initialize interfaces
GPIO.setup(POWER, GPIO.OUT)
GPIO.setup(INC, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Note: Pulled up internally
GPIO.setup(DEC, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Note: Pulled up internally
GPIO.setup(ZCROSS, GPIO.IN)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.output(TRIG, GPIO.LOW) # Initializes the triac as LOW/off (High, because of the external NPN inverter)

##### Global-scope "constants"
# Timing values are in microseconds
MINDELAY = 1000	# Minimum delay between zcrossing and firing
MAXDELAY = 6500 # Max delay. Output is held low/off when at MAXDELAY
PULSE = 500 	# Length of trigger pulse
STEPSIZE = 250	# Size of timing variation steps. 
STEPLIGHT = 100 # Size of timing steps for the light bulb profile
MOTORMIN = 5750 # Minimum delay for the motor dimmer profile
NUMSTEPS = 5 # Number of steps in the motor ramp up
STEPS90 = 10 # Number of steps till roughly 90v as measured on an RMS voltmeter
	
##### Global-scope variables
ledOn = 0	
delay = MAXDELAY


def zeroCross(channel):	# Interrupt handler for the positive-going zero crossing signal. Drives the triac.
	if(delay != MAXDELAY):
		time.sleep(delay/1000000)
		GPIO.output(TRIG, GPIO.HIGH)
		time.sleep(PULSE/1000000)
		GPIO.output(TRIG, GPIO.LOW)


def blink(condition):	# Status LED toggler or direct control via 0, 1, 2; or via False, True, and 2. 
	global ledOn
	if(condition == 2 and ledOn):
		blink(False)
	elif(condition):
		GPIO.output(POWER, GPIO.HIGH) # Turns on power LED on to indicate script is running. 3.3v max 16mA
		ledOn = 1
	elif(not condition):
		GPIO.output(POWER, GPIO.LOW) # Turns off power LED
		ledOn = 0
	else:
		blink(True)


def getSpeed(ramp):	# Controls the delay that the zero cross handler uses to do its thing.
	global delay
	global numTrigs
	blink(2)

	# Custom dimmer profiles
	if(ramp==4):	# Ramp up to 90v RMS.
		print('90v ramp enabled')
		numSteps = STEPS90
		ramp = 1
	else:
		numSteps = NUMSTEPS
	if(ramp==1):	# Ramp up numSteps steps. TODO: ramp up to a specific delay instead of # of steps.
		print('Motor Ramp Enabled')
		#delay = 5700
		#time.sleep(0.2)
		#delay = MAXDELAY - STEPSIZE
		for i in range(numSteps):
			time.sleep(0.5)
			delay -= STEPSIZE
			print('Delay:', delay, '\r', end='')
			blink(2)
		time.sleep(10)
	elif(ramp==2):	# Ramp up to the minimum delay
		print('Full Range Ramp Enabled')
		while(delay > MINDELAY):
			time.sleep(0.5)
			delay -= STEPSIZE
			print('Delay:', delay, '\r', end='')
			blink(2)
		time.sleep(10)
	elif(ramp==3):	# Ramp up to the brightest of a 40w bulb
		print('Light Bulb Ramp Enabled')
		while(delay > MINDELAY):
			time.sleep(0.1)
			delay -= STEPLIGHT
			print('Delay:', delay, '\r', end='')
			blink(2)
		time.sleep(10)
	delay = MAXDELAY
	print('Manual Mode started')
	print('Delay:', delay, '\r', end='')
	while(True):	# Main running loop. Blinks LED and polls for input
		blink(2)
		if(not GPIO.input(DEC) and delay > MINDELAY):
			delay -= STEPSIZE
			print('Delay:', delay, '\r', end='')
			time.sleep(0.4)
		elif(not GPIO.input(INC) and delay < MAXDELAY):
			delay += STEPSIZE
			print('Delay:', delay, '\r', end='')
			time.sleep(0.4)
		else:
			time.sleep(0.1)


def main():	# Main function
	getSpeed(dimmerProfile)
	while(True):
		blink(2)
		time.sleep(0.1)


if __name__ == '__main__':
	GPIO.add_event_detect(ZCROSS, GPIO.RISING, callback=zeroCross, bouncetime=3) # Setup for GPIO interrupt. Debounce is in milliseconds
	main()	
