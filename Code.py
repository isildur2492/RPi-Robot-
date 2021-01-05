#!/usr/bin/python

# Final Script to Control All functions of the Autonomous Robot

from picamera import PiCamera
from picamera.array import PiRGBArray
import RPi.GPIO as GPIO
import smtplib
import time
import math
import os

# Importing OpenCV
import cv2
import cv2.cv as cv

import numpy as np
import sys

# GPIO setup
GPIO.setmode(GPIO.BCM) # set as broadcom

# Define the BCM channels for sensors
sensor1 = 17 #green
sensor2 = 27 #red
sensor3 = 22 #yellow

# Define the BCM channel for the water pump
pump = 26

# Initialize the GPIOs 
GPIO.setup(sensor1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(sensor2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(sensor3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(6, GPIO.OUT)
GPIO.setup(13,GPIO.OUT)
GPIO.setup(5, GPIO.OUT)
GPIO.setup(pump, GPIO.OUT)


# Define the pulse, duty cycle, and frequency calculations
hc = 0.00130
hdcC = hc/(hc + 0.02)*100
hfrC = 1/(0.02 + hc)

ha = 0.00165
hdcA = ha/(ha + 0.02)*100
hfrA = 1/(0.02 + ha)

qc = 0.001472
qdcC = qc/(qc + 0.02)*100
qfrC = 1/(0.02 + qc)

qa = 0.00155
qdcA = qa/(qa + 0.02)*100
qfrA = 1/(0.02 + qa)

pulse = 0.0015
dc = pulse/(pulse+ 0.02)*100
fr = 1/(0.02 + pulse)

pL = GPIO.PWM(6,fr)
pR = GPIO.PWM(13,fr)
arm = GPIO.PWM(5,fr)

# Start servos as close to stop
pL.start(0)
pR.start(0)
arm.start(0)

# FUNCTIONS
def moveArm(t):
	arm.ChangeDutyCycle(qdcC)
	arm.ChangeFrequency(qfrC)
	curTime = time.time() + t
	while time.time() < curTime:
		pass
	arm.ChangeDutyCycle(0)

def backArm(t):
	arm.ChangeDutyCycle(qdcA)
	arm.ChangeFrequency(qfrA)
	curTime = time.time() + t
	while time.time() < curTime:
		pass
	arm.ChangeDutyCycle(0)

def turnLeftSlow(t):
	pL.ChangeDutyCycle(hdcC)
	pL.ChangeFrequency(hfrC)
	pR.ChangeDutyCycle(hdcC)
	pR.ChangeFrequency(hfrC)
	curTime = time.time() + t
	while time.time() < curTime:
		pass
	pL.ChangeDutyCycle(0)
	pR.ChangeDutyCycle(0)
	return

def turnRightSlow(t):
	pL.ChangeDutyCycle(hdcA)
        pL.ChangeFrequency(hfrA)
        pR.ChangeDutyCycle(hdcA)
        pR.ChangeFrequency(hfrA)
        curTime = time.time() + t
        while time.time() < curTime:
                pass
        pL.ChangeDutyCycle(0)
        pR.ChangeDutyCycle(0)
        return


# Green Sensor callback
def sensor1_callback(channel):
	if GPIO.input(channel):
		print "sensor1 on"
	else:
		print "sensor1 off"
		if("sensor1" not in needsWater):
			needsWater.append("sensor1")
# Red Sensor callback
def sensor2_callback(channel):
	if GPIO.input(channel):	
		print "sensor2 on"
	else:
		print "sensor2 off"
		if("sensor2" not in needsWater):
			needsWater.append("sensor2")
		

# Yellow Sensor callback
def sensor3_callback(channel):
	if GPIO.input(channel):
		print "sensor3 on"
	else:
		print "sensor3 off"
		if("sensor3" not in needsWater):
			needsWater.append("sensor3")




GPIO.add_event_detect(sensor1, GPIO.FALLING, callback=sensor1_callback, bouncetime=300)
GPIO.add_event_detect(sensor2, GPIO.FALLING, callback=sensor2_callback, bouncetime=300)
GPIO.add_event_detect(sensor3, GPIO.FALLING, callback=sensor3_callback, bouncetime=300)

# Define OpenCV capture video
cap = cv2.VideoCapture(0)


# Define the queue
needsWater = []
i = 0

now = time.time()
adjust = 1

# Define cx and cy
cx = -1
cy = -1

# Start with state 0, initializing, and try to find (non-existant black tag)
state = 0
findColor = 'black'
blackLB = (0,0,0)
blackUB = (0,0,0)
colorLB = blackLB
colorUB = blackUB

# Define the half size of the screen
halfScreen = 350

##### INITIALIZE VIDEO AND CAPTURE TO RGB MATRIX #####

global camera, rawCapture
camera = PiCamera()
camera.framerate = 15
rawCapture = PiRGBArray(camera)
time.sleep(0.5)

########### COLOR MAIN LOOP RECOGNITION ##############

pixel_size = 200
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port = True):
	image = frame.array
	imageRaw = image.copy()
	greenLB= (50,100,0)
        greenUB = (100, 255, 140)

        redLB = (169,136,103)
        redUB = (179,225, 206)

        yellowLB = (10,50,100)
        yellowUB = (80,230,230)

        if(findColor == "red"):
                colorLB = redLB
                colorUB = redUB

        elif(findColor == "yellow"):
                colorLB = yellowLB
                colorUB = yellowUB

        elif(findColor == "green"):
                colorLB = greenLB
                colorUB = greenUB
        else:
                colorLB = blackLB
		colorUB = blackUB

	hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, colorLB, colorUB)
        mask = cv2.erode(mask, None, iterations =2 )
        mask = cv2.dilate(mask, None , iterations =2 )

	# Ensure no stray element is detected as tag
	contours = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]

        for c in contours:
                if cv2.contourArea(c) > pixel_size:

        ################# CENTROID OF THE TAG ##################
                        M = cv2.moments(c)
                        cx = int(M["m10"]/ M["m00"])
                        cy = int(M["m01"] / M["m00"])

			# Define contour and center
                        cv2.drawContours(image, [c] , -1, (0,255,255), 2 )
                        cv2.circle(image, (cx,cy), 7, (255,255,255), -1 )

	# Display on console for debugging
        #cv2.imshow("RAW", imageRaw)
        #cv2.imshow("Threshold", mask)
        #cv2.imshow("overlay", image)

        print cx, cy
	key = cv2.waitKey(1) & 0xFF
        rawCapture.truncate(0)
	
        if( key == ord("q") ):
                break

	print needsWater
	print state
	print findColor

###################### STATE MACHINE #########################

	# STATE 0: Initializing
	if state == 0:
		if needsWater == []:
			findColor = 'black'
			cx = -1
			cy = -1
		elif needsWater[0]=='sensor2':
			cx = -1
			cy = -1
			state = 4
			findColor = 'red'
		elif needsWater[0] == 'sensor1':
			cx = -1
			cy = -1
			state = 2
			move = 1
			findColor = 'green'
		elif needsWater[0] == 'sensor3':
			cx = -1
			cy = -1
			state = 1
			move = 1
			findColor = 'yellow'
		else:
			findColor = 'black'
			cx = -1
			cy = -1
	
	# STATE 1:  Turn Left towards Yellow/Sensor3
	elif state == 1:
		if cx > 0 and cy > 0:
			state = 3
		elif move == 1:
			turnLeftSlow(0.3)
			now = time.time() + 1
			move = 0
		elif time.time() >= now:
			move = 1
		else:
			pass

	# STATE 2: Turn Right towards Green/Sensor1
        elif state == 2:
                if cx > 0 and cy > 0:
                        state = 3
                elif move == 1:
                        turnRightSlow(0.2)
                        now = time.time() + 1
                        move = 0
                elif time.time() >= now:
                        move = 1
                else:
                        pass
	
	# STATE 3: Adjusting
	elif state == 3:
		if cx < (halfScreen*1.1) and cx > (halfScreen*0.9):
			if findColor == 'yellow' or findColor == 'green':
				state = 4
			elif findColor == 'red':
				state = 0
			else:
				pass

		elif cx > (halfScreen*1.1) and adjust == 1:
			turnRightSlow(0.1)
			adjust = 0
			adjustTime = time.time() + 1
		elif cx < (halfScreen*0.9) and adjust == 1:
			turnLeftSlow(0.1)
			adjust = 0
			adjustTime = time.time() + 1
		else:
			if time.time() >= adjustTime:
				adjust = 1
	
	# STATE 4: WATERING PLANT
	elif state == 4:
		
		# Lowers arm and turns on pump
		moveArm(0.7)
		GPIO.output(pump, True)
		time.sleep(1)

		# Turns off pump and raises arm
		GPIO.output(pump, False)
		backArm(0.6)

		# Remove from queue
		if(findColor == 'red'):
			needsWater.remove('sensor2')
			print 'Was here'	
		elif(findColor == 'green'):
			needsWater.remove('sensor1')
			print 'remove sensor1'
		
		elif(findColor == 'yellow'):
			needsWater.remove('sensor3')
			print 'remove sensor3'
		else:
			pass
		state = 5	

	# STATE 5: Return to center
	elif state == 5:
		if findColor ==  'yellow':
			findColor = 'red'
			cx = -1
			cy = -1
			state = 2
		elif findColor == 'green':
			findColor = 'red'
			cx = -1
			cy = -1
			state = 1 
		# If red
		else:
			state = 0
			cx = -1
			cy = -1
			findColor = 'black'
	  