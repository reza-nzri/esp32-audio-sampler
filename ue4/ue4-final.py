# Übungsblatt 4 - Finale Abgabe

'''
Versteht die D/A-Wandlung (Digital-Analog-Wandlung) mit PWM.

Dieses Programm erzeugt digitale Samples und gibt sie über PWM wieder aus.
Der ESP32 benutzt dabei GPIO0 als PWM-Ausgang.

1. ESP32 wird auf 240 MHz gesetzt.
2. PWM wird mit 100 kHz gestartet.
3. Digitale Sinus-Samples werden erzeugt.
4. Die Samples werden nacheinander als Duty-Cycle ausgegeben.
5. Dadurch entsteht nach einem Tiefpass ein analoges Signal.

PWM:
Der ESP32 schaltet den Ausgang sehr schnell zwischen AN und AUS.
Der Duty-Cycle bestimmt den Mittelwert der Spannung.

0 % Duty → immer AUS → 0 V.
50 % Duty → halb AN, halb AUS → etwa halbe Spannung.
100 % Duty → immer AN → maximale Spannung.

Mit PWM und einem Tiefpass kann man also einen einfachen DAC nachbilden.
'''

import machine                         # ESP32-Systemfunktionen
import time                            # Zeitfunktionen
from machine import Pin                # GPIO-Pins
from machine import PWM                # PWM-Modul
from machine import Timer              # Timer-Modul
from machine import ADC                # ADC-Modul
import math                            # Mathematische Funktionen


class Sampler():

    # Klassenvariablen
    adc = ADC(Pin(34), atten=ADC.ATTN_11DB)    # ADC auf GPIO34
    pwm_pin = PWM(Pin(0))                      # PWM-Ausgang auf GPIO0
    tim = Timer(0)                             # Timer 0 benutzen
    samples = []                               # Liste für digitale Samples
    conv = False                               # Status der Wandlung

    def __init__(self, fs):

        # ESP32 auf maximale Taktfrequenz setzen
        machine.freq(240000000)

        # PWM mit 100 kHz und 50 % Duty-Cycle starten
        Sampler.pwm_pin.init(int(1E5), duty_u16=32768)

        # kurze Wartezeit
        time.sleep_ms(50)

        # Abtastfrequenz speichern
        self.fs = fs

    def pwm(self, duty):
        '''
        Startet ein PWM-Signal.
        duty: Tastverhältnis zwischen 0 und 65535
        '''

        # Prüfen, ob duty im erlaubten Bereich liegt
        if (duty < 0) or (duty > 65535):
            raise Exception("Duty-Cycle must be in between [0,65535]%!")

        # Duty-Cycle setzen
        Sampler.pwm_pin.duty_u16(int(duty))

    def convDA(self):

        # Alle Samples nacheinander ausgeben
        for duty in Sampler.samples:

            # aktuelles Sample als PWM-Duty ausgeben
            self.pwm(duty)

            # bis zum nächsten Timer-Aufruf warten
            yield

    def handler(self, gen):

        try:
            # nächstes Sample ausgeben
            next(gen)

        except StopIteration:
            # Timer stoppen, wenn alle Samples ausgegeben wurden
            Sampler.tim.deinit()

            # Wandlung ist beendet
            self.conv = False

    def startDA(self):

        # Generator für D/A-Wandlung erzeugen
        gen = self.convDA()

        # Status auf laufend setzen
        self.conv = True

        # Timer startet Ausgabe mit der Abtastfrequenz fs
        Sampler.tim.init(mode=Timer.PERIODIC, freq=self.fs, callback=lambda t:self.handler(gen))


if __name__ == "__main__":

    # Abtastfrequenz auf 5 kHz setzen
    fs = 5000

    # Sampler-Objekt erzeugen
    sampler = Sampler(fs)

    # Testfrequenzen
    frequencies = [100, 440, 1000]

    # Endlosschleife für wiederholte Ausgabe
    while True:

        # jede Frequenz nacheinander testen
        for f in frequencies:

            # aktuelle Frequenz ausgeben
            print("Spiele", f, "Hz")

            # digitale Sinus-Samples erzeugen
            Sampler.samples = [
                32767 * math.sin(2 * math.pi * f / fs * n) + 32768
                for n in range(int(fs / f))
            ]

            # D/A-Wandlung starten
            sampler.startDA()

            # warten bis Ausgabe fertig ist
            while sampler.conv:
                pass

            # kurze Pause zwischen den Tönen
            time.sleep(2)