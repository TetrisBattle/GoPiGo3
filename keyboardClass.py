import random
import easygopigo3 as easy
import threading
from time import sleep

from easygopigo3 import EasyGoPiGo3
easyGPG = EasyGoPiGo3()
import gopigo3
GPG = gopigo3.GoPiGo3()

class keyboard(object):
    KEY_DESCRIPTION = 0
    KEY_FUNC_SUFFIX = 1

    left_blinker_on = False
    right_blinker_on = False

    left_eye_on = False
    right_eye_on = False
    
    speed = 300
    servoPos = 1450

    def __init__(self):
        self.gopigo3 = easy.EasyGoPiGo3()
        self.keybindings = {
            "w" : ["Aja eteen pain", "forward"],
            "s" : ["Aja taakse pain", "backward"],
            "a" : ["Kaanny vasemmalle", "left"],
            "d" : ["Kaanny oikealle", "right"],
            "<SPACE>" : ["Pysahdy", "stop"],
            
            "q" : ["Kaarra vasemmalle (Jos max nopeus on paalla)", "steerLeft"],
            "e" : ["Kaarra oikealle (Jos max nopeus on paalla)", "steerRight"],
            
            "1" : ["Minimi nopeus", "speedSlow"],
            "2" : ["Normaali nopeus", "speedNormal"],
            "3" : ["Max nopeus", "speedFast"],
            
            "4" : ["Kaanna kameraa vasemmalle", "servoPosLeft"],
            "5" : ["Suorista kamera", "servoPosMiddle"],
            "6" : ["Kaanna kameraa oikealle", "servoPosRight"],
            
            "7" : ["Etuvalot ON/OFF", "blinkers"],
            "8" : ["Lamput ON/OFF", "eyes"],
            "9" : ["Vaihda lamppujen varia", "eyescolor"],
            
            "0" : ["Automaatti ohjaus", "Automation"],
            
            "<ESC>" : ["Exit", "exit"],
        }
        
        self.order_of_keys = [
            "w", "s", "a", "d", "<SPACE>", "q", "e", 
            "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "<ESC>"
        ]

    def executeKeyboardJob(self, argument):
        method_prefix = "function_"
        try:
            method_suffix = str(self.keybindings[argument][self.KEY_FUNC_SUFFIX])
        except KeyError:
            method_suffix = ""
        method_name = method_prefix + method_suffix

        method = getattr(self, method_name, lambda : "nothing")

        return method()

    def drawMenu(self):
        try:
            for key in self.order_of_keys:
                print("\r{:8} =  {}".format(key, self.keybindings[key][self.KEY_DESCRIPTION]))
        except KeyError:
            print("Error: Keys found GoPiGo3WithKeyboard.order_of_keys don't match with those in GoPiGo3WithKeyboard.keybindings.")
        
    def function_forward(self):
        self.gopigo3.forward()
        return "moving"

    def function_backward(self):
        self.gopigo3.backward()
        return "moving"

    def function_left(self):
        self.gopigo3.left()
        return "moving"

    def function_right(self):
        self.gopigo3.right()
        return "moving"

    def function_stop(self):
        self.gopigo3.stop()
        return "moving"
    
    def function_steerLeft(self):
        easyGPG.steer(30,50)
        return "moving"
    
    def function_steerRight(self):
        easyGPG.steer(50,30)
        return "moving"
    
    def function_servoPosLeft(self):
        if self.servoPos < 2400:
            self.servoPos += 20
            GPG.set_servo(GPG.SERVO_1, self.servoPos)
        return "static"
    
    def function_servoPosMiddle(self):
        self.servoPos = 1450
        GPG.set_servo(GPG.SERVO_1, self.servoPos)
        return "static"
    
    def function_servoPosRight(self):
        if self.servoPos > 570:
            self.servoPos -= 20
            GPG.set_servo(GPG.SERVO_1, self.servoPos)
        return "static"
    
    def function_speedSlow(self):
        speed = 150
        easyGPG.set_speed(speed)
        return "static"
    
    def function_speedNormal(self):
        speed = 300
        easyGPG.set_speed(speed)
        return "static"
    
    def function_speedFast(self):
        speed = 500
        easyGPG.set_speed(speed)
        return "static"

    def function_blinkers(self):
        if self.left_blinker_on is False and self.right_blinker_on is False:
            self.gopigo3.led_on(0)
            self.gopigo3.led_on(1)
            self.left_blinker_on = self.right_blinker_on = True
        else:
            self.gopigo3.led_off(0)
            self.gopigo3.led_off(1)
            self.left_blinker_on = self.right_blinker_on = False
        return "static"

    def function_eyes(self):
        if self.left_eye_on is False and self.right_eye_on is False:
            self.gopigo3.open_eyes()
            self.left_eye_on = self.right_eye_on = True
        else:
            self.gopigo3.close_eyes()
            self.left_eye_on = self.right_eye_on = False
        return "static"

    def function_eyescolor(self):
        red = random.randint(0, 255)
        green = random.randint(0, 255)
        blue = random.randint(0, 255)

        self.gopigo3.set_eye_color((red, green, blue))
        if self.left_eye_on is True:
            self.gopigo3.open_left_eye()
        if self.right_eye_on is True:
            self.gopigo3.open_right_eye()
        return "static"
    
    def function_Automation(self):
        return "automation"

    def function_exit(self):
        return "exit"

