from __future__ import print_function
from __future__ import division

from keyboardClass import keyboard

import threading
import sys

from curtsies import Input
import signal

from time import sleep
from easygopigo3 import EasyGoPiGo3
easyGPG = EasyGoPiGo3()
import gopigo3
GPG = gopigo3.GoPiGo3()
from di_sensors.easy_distance_sensor import EasyDistanceSensor
distanceSensor = EasyDistanceSensor()

automated = 0

def resetServoAndMove():
    GPG.set_servo(GPG.SERVO_1, 1450)
    distance = 101
    sleep(0.1)
    easyGPG.forward()

def steerLeft(wallAhead):
    easyGPG.steer(25,30)
    sleep(0.5)
    easyGPG.forward()

def steerRight(wallAhead):
    easyGPG.steer(30,25)
    sleep(0.5)
    easyGPG.forward()

def automation():
    global automated
    continueAutomation = False

    msDefault = 300

    servoLeft = 2400
    servoMiddle = 1450
    servoRight = 570

    turnAble = 40
    wallAhead = 15
    wallLeft = 20
    x = 5
    delay = 0.2
    
    while True:
        if automated == 2:
            sys.exit()
        elif automated == 0:
            #print("idle")
            sleep(0.2)
        else:
            GPG.reset_all()
            sleep(0.2)
            GPG.set_led(GPG.LED_WIFI, 50, 0, 50) # purple light at start
            GPG.set_servo(GPG.SERVO_1, servoMiddle)
            easyGPG.set_speed(msDefault)
            easyGPG.forward()

            while automated == 1:
                distance = distanceSensor.read()
                if distance < wallAhead:
                    easyGPG.stop()
                    GPG.set_servo(GPG.SERVO_1, servoRight)
                    sleep(delay)
                    distance = distanceSensor.read()
                    if distance > turnAble:
                        continueAutomation = True
                        easyGPG.turn_degrees(90, True)
                        resetServoAndMove()
                        break
                    else:
                        GPG.set_servo(GPG.SERVO_1, servoMiddle)
                        automated = 0
                        print("Automation OFF (Oikealle ei voi kaantya joten automaatti mode sammutetaan.)")
                        break
                    
            if continueAutomation == True:
                GPG.set_led(GPG.LED_WIFI, 0, 50, 0) # green = start the loop
                while automated == 1:
                    distance = distanceSensor.read()
                    if distance < 10:
                        GPG.set_servo(GPG.SERVO_1, servoRight)
                        sleep(delay)
                        easyGPG.backward()
                        while distance < turnAble and automated == 1:
                            distance = distanceSensor.read()
                        easyGPG.turn_degrees(90, True)
                    elif distance < 70:
                        GPG.set_led(GPG.LED_WIFI, 0, 0, 50) # blue = wall
                        easyGPG.drive_cm(distance - wallAhead, True)
                        easyGPG.stop()
                        GPG.set_servo(GPG.SERVO_1, servoLeft)
                        sleep(delay)
                        distance = distanceSensor.read()
                        if distance > turnAble+20:
                            easyGPG.turn_degrees(-90, True)
                        else:
                            GPG.set_servo(GPG.SERVO_1, servoRight)
                            sleep(0.2)
                            distance = distanceSensor.read()
                            if distance > turnAble:
                                easyGPG.turn_degrees(90, True)
                            else:
                                easyGPG.backward()
                                while distance < turnAble and automated == 1:
                                    distance = distanceSensor.read()
                                easyGPG.turn_degrees(90, True)
                    else:
                        GPG.set_led(GPG.LED_WIFI, 50, 50, 0) # yellow = checking blocks
                        GPG.set_servo(GPG.SERVO_1, servoLeft)
                        sleep(delay)
                        distance = distanceSensor.read()
                        if distance > turnAble:
                            GPG.set_led(GPG.LED_WIFI, 50, 0, 0) # red = open space at left
                            easyGPG.drive_cm(20, True)
                            easyGPG.turn_degrees(-90, True)
                        elif distance < wallLeft-x:
                            GPG.set_led(GPG.LED_EYE_LEFT, 50, 50, 0) #yellowLeft = turning
                            steerRight(wallLeft-x)
                            GPG.set_led(GPG.LED_EYE_LEFT, 0, 0, 0)
                        elif distance > wallLeft+x:
                            GPG.set_led(GPG.LED_EYE_RIGHT, 50, 50, 0) #yellowRight = turning
                            steerLeft(wallLeft+x)
                            GPG.set_led(GPG.LED_EYE_RIGHT, 0, 0, 0)
                    resetServoAndMove()
            automated = 0

def Main():
    global automated
    
    t = threading.Thread(target=automation)
    t.start()
    
    project = keyboard()
    project.drawMenu()
    
    GPG.reset_all()
    sleep(0.2)
    easyGPG.set_speed(300)
    GPG.set_servo(GPG.SERVO_1, 1450)
    
    result = "nothing"
    manual_mode = False
    successful_exit = True
    refresh_rate = 20.0

    with Input(keynames = "curtsies", sigint_event = True) as input_generator:
        while True:
            period = 1 / refresh_rate
            key = input_generator.send(period)

            if key is not None:
                if automated == 1:
                    automated = 3
                    while automated != 0:
                        print("automation shutting down...")
                        sleep(1)
                    GPG.reset_all()
                    sleep(0.2)
                    GPG.set_servo(GPG.SERVO_1, 1450)
                    easyGPG.set_speed(300)
                    print("automation OFF")
                    if key == "<ESC>":
                        automated = 2
                        sleep(0.5)
                        GPG.reset_all()
                        break
                else:
                    result = project.executeKeyboardJob(key)
                    
                    if result == "automation":
                        if automated == 0:
                            automated = 1
                            print("automation ON")
                    
                    elif result == "exit":
                        automated = 2
                        sleep(0.5)
                        GPG.reset_all()
                        break
                
            elif manual_mode is True and result == "moving":
                project.executeKeyboardJob("x")


if __name__ == "__main__":
    # set up a handler for ignoring the Ctrl+Z commands
    signal.signal(signal.SIGTSTP, lambda signum, frame : print("Press the appropriate key for closing the app."))

    try:
        Main()
    except IOError as error:
        # if the project is not reachable
        # then print the error and exit
        print(str(error))
        exit(1)

    exit(0)