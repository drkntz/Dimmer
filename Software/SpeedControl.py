
# SpeedControl.py
# This is an attempt at a python script to monitor speed control. it needs to be run on a Pi
# Zach Martin, 28 Jul 2020
# 

import RPi.GPIO as GPIO
import time # an attempt to make sleeping work in a loop idk i'm not a scientist
from multiprocessing import Process, Queue # for running multiple things simultaneously-ish
import sys

GPIO.setmode(GPIO.BCM) # Uses the BCM pin definitions--Useful for different revisions of RPI's & not breaking code

# Giving BCM pin numbers a name
powerLed = 14
inc = 15
dec = 18
zCross = 23
trig = 24

# Setting up BCM pins as inputs or outputs
GPIO.setup(powerLed, GPIO.OUT)
GPIO.setup(inc, GPIO.IN)
GPIO.setup(dec, GPIO.IN)
GPIO.setup(zCross, GPIO.IN)
GPIO.setup(trig, GPIO.OUT)
GPIO.output(trig, GPIO.LOW) # initializes the trigger 


#delay = 1 # amount of delay between beginning of zcross pulse and actual zcrossing, abt 1 mS
minDelay = 1000 # the minimum speed. IE when the output is on
maxDelay = 6500 # the max speed of the output waveform. IE when the output is fully off
period = 8330
pulseLength = 500 # length of trigger pulse
blinkRate = 0.2 # Blink speed of LED
stepSize = 250
afterWait = 500
rampMax = 5750
NUMSTEPS = 5 # Number of steps in the motor ramp up
STEPS90 = 10 # number of steps till 90v

def delayus(uSec):
	sec = uSec/1000000
	time.sleep(uSec)

def blink():
	while(True):
		GPIO.output(powerLed, GPIO.HIGH) # Turns on power LED on to indicate script is running. 3.3v max 16mA
		time.sleep(blinkRate)
		GPIO.output(powerLed, GPIO.LOW)
		time.sleep(blinkRate)

def getSpeed(delQ):
	delay = maxDelay # Initialize at maximum delay
	delQ.put(delay)	# Initializes queue
	rampUp = open('rampUp.txt', 'r')
	for i in rampUp:
		print(i)
		ramp =int( i)
	rampUp.close()
	if(ramp==4):
		print('90v ramp enable')
		numsteps = STEPS90
		ramp = 1
	else:
		numsteps = NUMSTEPS
	if(ramp==1):
		print('Motor Ramp Enabled')
		for i in range(numsteps):
			time.sleep(0.5)
			delay -= stepSize
			delQ.put(delay)
		time.sleep(10)
		delQ.put(maxDelay)
	elif(ramp==2):
		print('Full Range Ramp Enabled')
		while(delay > minDelay):
			time.sleep(1)
			delay -= stepSize
			delQ.put(delay)
		delQ.put(maxDelay)
	elif(ramp==3):
		print('Bulb Ramp Enabled')
		while(delay > minDelay + 1000):
			time.sleep(0.1)
			delay -= 100
			delQ.put(delay)
	else:
		print('Speed Ramp not enabled')
		while(True):
			if(GPIO.input(dec) and delay  > minDelay): # decreases motor speed (increases delta between zcross and trig)
				delay -= stepSize
				delQ.put(delay)
				print(delay)
				time.sleep(0.4)

			elif(GPIO.input(inc) and delay < maxDelay): # Increases motor speed (decreases delta between zcross and trig)
				delay += stepSize
				delQ.put(delay)
				print(delay)
				time.sleep(0.4)
			else:
				continue


def runMotor(delQ):
	delay = delQ.get()

	while(True):
		if(not delQ.empty()):
			delay = delQ.get()
		if(delay == maxDelay):
			continue


		if(GPIO.input(zCross)):
			time.sleep(delay/1000000)
			GPIO.output(trig, GPIO.HIGH)
			time.sleep(pulseLength/1000000)
			GPIO.output(trig, GPIO.LOW)
			time.sleep(afterWait/1000000)

#		elif(GPIO.input(zCross) and speed >= 0.0075 and speed != minSpeed):
#			speed = speed - 0.00725
#			time.sleep(speed)
#			GPIO.output(trig, GPIO.LOW)
#			time.sleep(pulseLength)
#			GPIO.output(trig, GPIO.HIGH)
#			time.sleep(0.003)
#
#		elif(speed <= maxSpeed):
#			GPIO.output(trig, GPIO.LOW)
#
#		else:
#			GPIO.output(trig, GPIO.HIGH) # Speed is minimum so no trigger
		

def main():
	dQ = Queue()
	#rQ = Queue()
	#bQueue = Queue()
#	gr = Process(target=getRamp, args=(rQ,))
	g = Process(target=getSpeed, args=(dQ,))
	b = Process(target=blink)
	r = Process(target=runMotor, args=(dQ,))
#	gr.start()
	b.start()
	g.start()
	r.start()

if __name__ == '__main__':
	main()
