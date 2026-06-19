# Übungsblatt 4 - Aufgabe 2 g)

'''
PWM (Pulse Width Modulation) zu verstehen
Erzeugt auf dem ESP32 ein PWM-Signal mit 100 kHz und einstellbarem Duty Cycle als Grundlage für eine D/A-Wandlung

1. ESP32 wird gestartet.
2. Auf GPIO0 wird ein 100-kHz-PWM-Signal erzeugt.
3. Der Benutzer kann das Tastverhältnis (0–65535) festlegen.
4. Dadurch kann später z. B. über einen Tiefpass eine analoge Spannung bzw. ein Audiosignal erzeugt werden.

PWM:
Der ESP32 schaltet einen Pin sehr schnell zwischen AN und AUS.
Hier: 100.000 Mal pro Sekunde (100 kHz).

mit PWM und einem Tiefpass kann man einen einfachen DAC (Digital-Analog-Converter) nachbilden.
dies ist die Grundlage für spätere Audioausgabe und Signalverarbeitung

0 % Duty → immer AUS → 0 V.
50 % Duty → halb AN, halb AUS → etwa halbe Spannung.
100 % Duty → immer AN → maximale Spannung.
'''


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

    # 25 % Tastverhältnis einstellen
    sampler.pwm(16384)

    print("PWM gestartet.")