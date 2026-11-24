import RPi.GPIO as GPIO
import time
import numpy as np
GPIO.setmode(GPIO.BOARD) #definim pinii dupa numerotarea de pe board

Pin_microfon=13
Pin_led=11
Pin_buzzer=12

def setp_pins():
    GPIO.setup(Pin_microfon, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #setare pin microfon, e activ pe high, low-default
    GPIO.setup(Pin_led, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(Pin_buzzer, GPIO.OUT, initial=GPIO.LOW)
    print("configurat cu succes!")
    GPIO.cleanup()
setp_pins()

def read_microfon(duration):
    samples=[]
    end=time.monotonic()+duration
    while(time.monotonic()<end):
        samples.append(GPIO.input(Pin_led))
    return np.array(samples)
