# Übungsblatt 4 - Aufgabe 3 a)
# Gibt digitale Samples über PWM als analoges Signal aus.

import machine                         # ESP32-Funktionen
import time                            # Zeitfunktionen
from machine import Pin               # GPIO-Pins
from machine import PWM               # PWM-Modul
from machine import Timer             # Hardware-Timer
from machine import ADC               # ADC (wird hier noch nicht benutzt)
import math                           # Mathematische Funktionen

class Sampler():
    
    # Klassenvariablen
    adc = ADC(Pin(34), atten=ADC.ATTN_11DB)    # ADC auf GPIO34
    pwm_pin = PWM(Pin(0))                      # PWM-Ausgang auf GPIO0
    tim = Timer(0)                             # Timer 0
    samples = []                               # Liste für Samples
    conv = False                               # Status der Wandlung

    def __init__(self, fs):
        machine.freq(240000000)                # ESP32 auf 240 MHz setzen
        Sampler.pwm_pin.init(int(1E5), duty_u16=32768)  # PWM mit 100 kHz starten
        time.sleep_ms(50)                      # kurz warten
        self.fs = fs                           # Abtastfrequenz speichern
               
    def pwm(self, duty):
        '''
            Startet ein PWM-Signal.
            duty : Tastverhältnis von 0 bis 65535
        '''
        
        # Prüfen, ob der Wert gültig ist
        if (duty < 0) or (duty > 65535):
            raise Exception("Duty-Cycle must be in between [0,65535]%!")
        
        # PWM-Tastverhältnis setzen
        Sampler.pwm_pin.duty_u16(int(duty))
            
    def convDA(self):
        
        # Alle Samples nacheinander ausgeben
        for duty in Sampler.samples:
            
            # D/A-Wandlung conversation über PWM
            self.pwm(duty)
            
            # Bis zum nächsten Timer-Aufruf warten
            yield
            
    def handler(self,gen):
        try:
            # Nächstes Sample ausgeben
            next(gen)
            
        except StopIteration:
            # Timer stoppen
            Sampler.tim.deinit()
            
            # Wandlung beendet
            self.conv = False
        
    def startDA(self):
        
        # Generator erzeugen
        gen = self.convDA()
        
        # Wandlung läuft
        self.conv = True
        
        # Timer startet die Ausgabe mit der Abtastfrequenz
        Sampler.tim.init(
            mode=Timer.PERIODIC,
            freq=self.fs,
            callback=lambda t:self.handler(gen)
        )


if __name__ == "__main__":

    fs = 5000                          # Abtastfrequenz 5 kHz
    sampler = Sampler(fs)              # Sampler-Objekt erzeugen

    frequencies = [100, 440, 1000]     # Testfrequenzen aus Aufgabe 3b

    while True:                        # Endlosschleife für wiederholte Ausgabe

        for f in frequencies:          # jede Frequenz nacheinander testen

            print("Spiele", f, "Hz")   # aktuelle Frequenz anzeigen

            Sampler.samples = [        # Sinus-Samples erzeugen
                32767 * math.sin(2 * math.pi * f / fs * n) + 32768
                for n in range(int(fs / f))
            ]

            sampler.startDA()          # D/A-Wandlung starten

            while sampler.conv:        # warten bis Ausgabe fertig ist
                pass

            time.sleep(2)              # kurze Pause zwischen den Tönen