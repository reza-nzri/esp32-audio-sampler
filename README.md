# esp32-audio-sampler

ESP32 audio sampling and playback using MicroPython, PWM, and ADC.

## Setup

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
