# Übungsblatt 4 - Aufgabe 2 g)
# Erzeugt ein PWM-Signal mit 100 kHz und einstellbarem Tastverhältnis (Duty-Cycle).

import machine
import time
from machine import Pin
from machine import PWM

class Sampler():

    # PWM-Ausgang auf GPIO0
    pwm_pin = PWM(Pin(0))

    def __init__(self):

        # ESP32 auf maximale Taktfrequenz stellen
        machine.freq(240000000)

        # PWM mit 100 kHz starten und 50 % Tastverhältnis
        Sampler.pwm_pin.init(freq=100000, duty_u16=32768)

        # kurze Wartezeit
        time.sleep_ms(50)

    def pwm(self, duty):
        '''
        Startet ein PWM-Signal.
        duty: Tastverhältnis zwischen 0 und 65535
        '''

        # Bereich überprüfen
        if duty < 0 or duty > 65535:
            raise Exception("Duty muss zwischen 0 und 65535 liegen!")

        # PWM-Tastverhältnis setzen
        Sampler.pwm_pin.duty_u16(int(duty))


# Testprogramm
if __name__ == "__main__":

    # Objekt erzeugen
    sampler = Sampler()

    # 25 % Tastverhältnis
    sampler.pwm(16384)

    print("PWM gestartet.")