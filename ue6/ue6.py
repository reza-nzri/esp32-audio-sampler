# Übungsblatt 6 - Finale Abgabe

'''
Versteht das Aufnehmen, Abspielen und Speichern von Sprachproben mit dem ESP32.

Dieses Programm nutzt die Klasse Sampler aus Übung 4 und Übung 5.
Es nimmt Sprachproben über das Mikrofon auf, spielt sie wieder ab
und speichert die Samples in einer CSV-Datei auf dem ESP32.

1. ESP32 wird auf 240 MHz gesetzt.
2. Der ADC liest das Mikrofonsignal auf GPIO34 ein.
3. Die Samples werden in der Liste samples gespeichert.
4. Die Samples werden über PWM auf GPIO0 wiedergegeben.
5. Die Aufnahme kann in samples.csv gespeichert werden.
6. Die Datei samples.csv kann später mit Thonny auf den PC geladen werden.

Kurz:
Mikrofon → ADC → digitale Samples → PWM → Lautsprecher → CSV-Datei
'''

import machine                         # ESP32-Systemfunktionen
import time                            # Zeitfunktionen
from machine import Pin                # GPIO-Pins
from machine import PWM                # PWM-Modul
from machine import Timer              # Timer-Modul
from machine import ADC                # ADC-Modul
import gc                              # Speicherverwaltung
import io                              # Datei schreiben
import os                              # Dateisystem


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

            # Analogwert vom Mikrofon lesen und speichern
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

            # Timer stoppen, wenn Vorgang fertig ist
            Sampler.tim.deinit()

            # Status auf fertig setzen
            self.conv = False

    def startAD(self, T):

        # Generator für Aufnahme erzeugen
        gen = self.convAD(T)

        # Status auf laufend setzen
        self.conv = True

        # Timer startet Aufnahme mit Abtastfrequenz fs
        Sampler.tim.init(mode=Timer.PERIODIC, freq=self.fs, callback=lambda t:self.handler(gen))

    def startDA(self):

        # Generator für Wiedergabe erzeugen
        gen = self.convDA()

        # Status auf laufend setzen
        self.conv = True

        # Timer startet Wiedergabe mit Abtastfrequenz fs
        Sampler.tim.init(mode=Timer.PERIODIC, freq=self.fs, callback=lambda t:self.handler(gen))


if __name__ == "__main__":

    # Abtastfrequenz
    fs = 4000

    # Aufnahmezeit in Sekunden
    T = 4

    # Sampler-Objekt erzeugen
    sampler = Sampler(fs)

    # Dateiname für gespeicherte Samples
    fname = "samples.csv"

    # CSV-Datei zum Schreiben öffnen
    f = io.open(fname, "wt")

    # Endlosschleife für mehrere Sprachproben
    while True:

        # alte Samples löschen
        Sampler.samples.clear()

        # Speicher aufräumen
        gc.collect()

        # freien Speicher anzeigen
        print("Freier Speicher: {0}KiB".format(gc.mem_free() / 1024))

        # Benutzer entscheidet, ob Aufnahme startet oder Programm beendet wird
        eingabe = input("Drücke <ENTER> um Aufnahme zu starten. <q> + <ENTER> für beenden: ")

        # wenn q eingegeben wurde, Datei schließen und Programm beenden
        if eingabe == "q":
            f.close()
            break

        # Countdown vor Aufnahme
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

        # Benutzer kann Aufnahme anhören
        input("Drücke <ENTER> um Aufnahme anzuhören.")

        # Wiedergabe starten
        sampler.startDA()

        # Wiedergabe anzeigen
        print("Playback...")

        # warten bis Wiedergabe fertig ist
        while sampler.conv:
            pass

        # Wiedergabe fertig
        print("Done.")

        # Benutzer entscheidet, ob Aufnahme gespeichert wird
        eingabe = input("Drücke <ENTER> um Aufnahme zu speichern. <c> + <ENTER> für Verwerfen: ")

        # wenn nicht c eingegeben wurde, Aufnahme speichern
        if not eingabe == "c":

            # Name der Aufnahme eingeben
            smpnm = input("Bitte den Namen der Aufnahme eingeben: ")

            # Speichern anzeigen
            print("Storing...")

            # Name der Aufnahme zuerst schreiben
            f.write(smpnm + ",")

            # alle Samples bis auf das letzte schreiben
            for i in range(len(Sampler.samples) - 1):
                f.write(str(Sampler.samples[i]) + ",")

            # letztes Sample schreiben und Zeile beenden
            f.write(str(Sampler.samples[-1]) + "\n")

            # Speichern fertig
            print("Done.")
