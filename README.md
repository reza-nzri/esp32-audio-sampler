# esp32-audio-sampler

ESP32 audio sampling and playback using MicroPython, PWM, and ADC.

**Was das Projekt macht:**

- Ü4: PWM auf dem ESP32 verstehen, PWM als einfachen DAC nutzen, Sinustöne erzeugen und über PWM ausgeben. Das passt zu Übung 4: PWM-Generator, D/A-Wandlung und `convDA`.

- Ü5: Mikrofon über ADC aufnehmen und die Samples danach wieder über PWM abspielen. Das passt zu Übung 5: `convAD`, `startAD`, Aufnahmezeit `T` und Wiedergabe.

- Ü6: Sprachproben aufnehmen, in `samples.csv` speichern, mit Notebook plotten und Wortgrenzen/SNR untersuchen. Das passt zu Übung 6.

- `samples.csv` sollte für echte Abgabe mindestens **10 echte Sprachproben** enthalten, nicht nur Dummy-Daten.

<details>

<summary><h2>Setup</h2></summary>

### 1. Repository klonen

```bash
git clone https://github.com/reza-nzri/esp32-audio-sampler.git
cd esp32-audio-sampler
```

### 2. Virtuelle Umgebung erstellen

```bash
uv venv .venv
```

### 3. Virtuelle Umgebung aktivieren (Windows)

```powershell
.\.venv\Scripts\activate
```

### 4. Abhängigkeiten installieren

```bash
uv pip install -r requirements.txt
```

---

## Neue Bibliothek installieren

```bash
uv pip install <library-name>
```

Danach die `requirements.txt` aktualisieren:

```bash
uv pip freeze > requirements.txt
```

</details>
