# Übungsblatt 5 - Finale Abgabe

'''
Versteht die A/D-Wandlung (Analog-Digital-Wandlung) mit dem ESP32.

Dieses Programm nimmt ein Audiosignal über das Mikrofon auf
und gibt die aufgenommenen Samples danach über PWM wieder aus.

1. ESP32 wird auf 240 MHz gesetzt.
2. Der ADC liest das Mikrofonsignal auf GPIO34 ein.
3. Die Samples werden in der Liste samples gespeichert.
4. Die gespeicherten Samples werden danach über PWM auf GPIO0 ausgegeben.
5. Dadurch kann eine einfache Aufnahme und Wiedergabe umgesetzt werden.

ADC:
Der ADC wandelt ein analoges Eingangssignal in digitale Zahlenwerte um.

PWM:
Die gespeicherten digitalen Werte werden als Duty-Cycle ausgegeben.
Mit PWM und einem Tiefpass kann daraus wieder ein analoges Signal entstehen.

Kurz:
Mikrofon → ADC → digitale Samples → PWM → Lautsprecher
'''

import machine                         # ESP32-Systemfunktionen
import time                            # Zeitfunktionen
from machine import Pin                # GPIO-Pins
from machine import PWM                # PWM-Modul
from machine import Timer              # Timer-Modul
from machine import ADC                # ADC-Modul
import gc                              # Speicherverwaltung


class Sampler():

    # Klassenvariablen
    adc = ADC(Pin(34), atten=ADC.ATTN_11DB)    # ADC auf GPIO34 für Mikrofon
    pwm_pin = PWM(Pin(0))                      # PWM-Ausgang auf GPIO0 für Lautsprecher
    tim = Timer(0)                             # Timer 0 benutzen
    samples = []                               # Liste für aufgenommene Samples
    conv = False                               # Status: Aufnahme/Wiedergabe läuft oder nicht

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

    def convAD(self, T):

        # Anzahl der Samples berechnen
        for i in range(T * self.fs):

            # Analogwert vom Mikrofon lesen und als digitales Sample speichern
            Sampler.samples.append(Sampler.adc.read_u16())

            # bis zum nächsten Timer-Aufruf warten
            yield

    def convDA(self):

        # Alle gespeicherten Samples nacheinander ausgeben
        for duty in Sampler.samples:

            # aktuelles Sample als PWM-Duty ausgeben
            self.pwm(duty)

            # bis zum nächsten Timer-Aufruf warten
            yield

    def handler(self, gen):

        try:
            # nächstes Sample aufnehmen oder ausgeben
            next(gen)

        except StopIteration:
            # Timer stoppen, wenn Aufnahme oder Wiedergabe fertig ist
            Sampler.tim.deinit()

            # Vorgang ist beendet
            self.conv = False

    def startAD(self, T):

        # Generator für A/D-Wandlung erzeugen
        gen = self.convAD(T)

        # Status auf laufend setzen
        self.conv = True

        # Timer startet Aufnahme mit der Abtastfrequenz fs
        Sampler.tim.init(mode=Timer.PERIODIC, freq=self.fs, callback=lambda t:self.handler(gen))

    def startDA(self):

        # Generator für D/A-Wandlung erzeugen
        gen = self.convDA()

        # Status auf laufend setzen
        self.conv = True

        # Timer startet Wiedergabe mit der Abtastfrequenz fs
        Sampler.tim.init(mode=Timer.PERIODIC, freq=self.fs, callback=lambda t:self.handler(gen))


if __name__ == "__main__":

    # Speicher aufräumen
    gc.collect()

    # freien Speicher anzeigen
    print("Freier Speicher: {0}KiB".format(gc.mem_free() / 1024))

    # Abtastfrequenz
    fs = 4000

    # Aufnahmezeit in Sekunden
    T = 4

    # Sampler-Objekt erzeugen
    sampler = Sampler(fs)

    # kurze Start-Wartezeit
    for wait in range(3, 0, -1):

        # Countdown anzeigen
        print("Sampling starts in {0} seconds...".format(wait))

        # 1 Sekunde warten
        time.sleep(1)

    # Aufnahme starten
    print("Recording...")

    # Startzeit speichern
    start_ticks = time.ticks_ms()

    # A/D-Wandlung starten
    sampler.startAD(T)

    # warten bis Aufnahme fertig ist
    while sampler.conv:
        pass

    # Endzeit speichern
    end_ticks = time.ticks_ms()

    # Aufnahme-Informationen ausgeben
    print("Sampling after T={0} sec. finished ({1} samples, {2}KiB).".format(
        time.ticks_diff(end_ticks, start_ticks) / 1000,
        len(Sampler.samples),
        len(Sampler.samples) * 2 / 1024
    ))

    # Wiedergabe-Endlosschleife
    while True:

        # Wiedergabe starten
        sampler.startDA()

        # Text ausgeben
        print("Playback...")

        # warten bis Wiedergabe fertig ist
        while sampler.conv:
            pass

        # Wiedergabe fertig
        print("Done.")

        # 2 Sekunden Pause
        time.sleep(2)
