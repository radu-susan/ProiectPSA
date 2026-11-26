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
prag_dB=9
P_ref_minim=0.1 #caz pt liniste 0%, la care nu putem imparti
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
def nivel_db(p, p_ref):
    p=max(p, 0.01)
    return 10*np.log10(p/p_ref)

def calibrate(seconds):
    levels = []
    for _ in range(int(seconds / FEREASTRA)):
        levels.append(procent_zgomot(read_microfon(FEREASTRA)))
    levels = np.array(levels)
    p_ref=max(levels.mean(), P_ref_minim)
    db_max=nivel_db(levels.max(), p_ref)
    db_std=10*np.log10(1+levels.std()/p_ref)
    print(f"Liniște: medie {levels.mean():.2f} %, max {levels.max():.2f} %")
    print(f"Referință 0 dB = {p_ref:.2f} %")
    print(f"Vârf în liniște: {db_max:+.1f} dB, variație: ±{db_std:.1f} dB")
    print(f"Prag ales: {prag_dB} dB")
    if db_max >= prag_dB:
        print("Atenție: liniștea a atins pragul. Alarma poate porni singură, "
          "mărește prag_dB.")
    return p_ref



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
        print("Se calibreaza 5 sec")
        p_ref=calibrate(5)
        peste_prag=0
        while True:
            p = procent_zgomot(read_microfon(FEREASTRA))
            db=nivel_db(p, p_ref)
            print(f"{p:.2f} %  ->  {db:+.1f} dB")
            if db > prag_dB:
                peste_prag += 1
            else:
                peste_prag = 0
            if peste_prag >= 2:
                peste_prag = 0
                print("ALARMĂ!")
                alarma(durata_alarma)
                time.sleep(pauza)
    except KeyboardInterrupt: pass
    finally:
        GPIO.cleanup()
if __name__ == "__main__":
    main()
