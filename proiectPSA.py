import RPi.GPIO as GPIO
import time
import numpy as np
GPIO.setmode(GPIO.BOARD) #definim pinii dupa numerotarea de pe board

Pin_microfon=13
Pin_led=11
Pin_buzzer=12
durata_alarma=3
pauza=1
FEREASTRA=0.1
MARJA_MINIMA=8
def setp_pins():
    GPIO.setup(Pin_microfon, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #setare pin microfon, e activ pe high, low-default
    GPIO.setup(Pin_led, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(Pin_buzzer, GPIO.OUT, initial=GPIO.LOW)
#setp_pins()

def read_microfon(duration):
    samples=[]
    end=time.monotonic()+duration #functie care practic masoara timp crescator
    while(time.monotonic()<end):
        samples.append(GPIO.input(Pin_microfon))
    return np.array(samples)

def procent_zgomot(samples):
    try:
        return 100*np.count_nonzero(samples)/samples.size #pentru ca pinul digital preia doar 0 si 1
    except ZeroDivisionError: return 0

def calibrate(seconds):
    levels = []
    for _ in range(int(seconds / FEREASTRA)):
        levels.append(procent_zgomot(read_microfon(FEREASTRA)))
    levels = np.array(levels)
    baza = levels.mean()
    marja = max(3 * levels.std(),
                levels.max() - levels.min(),
                MARJA_MINIMA)
    return baza, marja  #calibrare in functie de zgomotul din incapere, optional, valori pot fi hardcodate

def alarma(duration):
    GPIO.output(Pin_led, GPIO.HIGH)
    end = time.monotonic() + duration
    while (time.monotonic() < end):
        GPIO.output(Pin_buzzer, GPIO.HIGH)
        time.sleep(0.2)
        GPIO.output(Pin_buzzer, GPIO.LOW)
        time.sleep(0.2)
    GPIO.output(Pin_buzzer, GPIO.LOW)
    GPIO.output(Pin_led, GPIO.LOW)

#alarma(3)

def main():
    setp_pins()
    try:
        print("Se calibreaza")
        #baza, marja=calibrate(5)
        baza, marja=0, 3 #valoarea masurata pentru baza, asta detecteaza la kiniste, nu-l mai schimb ca de abia am setat potentiometrul
        peste_prag = 0
        while True:
            p = procent_zgomot(read_microfon(FEREASTRA))
            abatere = abs(p - baza)
            print(f"{p:.2f} %  (abatere {abatere:.2f})")
            if abatere > marja:
                peste_prag += 1
            else:
                peste_prag = 0
            if peste_prag >= 1:
                peste_prag = 0
                print("ALARMĂ!")
                alarma(durata_alarma)
                time.sleep(pauza)
    except KeyboardInterrupt: pass
    finally:
        GPIO.cleanup()
if __name__ == "__main__":
    main()
