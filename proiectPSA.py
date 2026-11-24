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
setp_pins()

def read_microfon(duration):
    samples=[]
    end=time.monotonic()+duration
    while(time.monotonic()<end):
        samples.append(GPIO.input(Pin_led))
    return np.array(samples)

def procent_zgomot(samples):
    try:
        return 100*np.count_nonzero(samples)/samples.size
    except ZeroDivisionError: return 0

def calibrate(seconds):
    levels=[]
    for i in range(seconds):
        levels.append(procent_zgomot(read_microfon(seconds)))
    levels = np.array(levels)
    prag=levels.mean()+3*levels.std()
    prag=max(prag, 0.2)
    return prag

def alarma(duration):
    GPIO.output(Pin_led, GPIO.HIGH)
    end = time.monotonic() + duration
    while (time.monotonic() < end):
        GPIO.output(Pin_buzzer, GPIO.HIGH)
        time.sleep(0.2)
        GPIO.output(Pin_buzzer, GPIO.LOW)
        time.sleep(0.2)
    GPIO.output(Pin_buzzer, GPIO.LOW)

#alarma(3)
