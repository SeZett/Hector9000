# Hector9001 - individualisierter Fork

Diese Version wurde angepasst für die Verwendung mit:

- Raspberry Pi 3
- PCA9685 Servotreiber
- HX711 Wägezelle
- Relaismodule zum Schalten der Servo-Stromversorgung und Pumpe

## Hardware Pin-Out
[Pin-Out](docs/hardware_pinout.md)


# Architektur
## HectorServer – Hardwaresteuerung & Sensorik

Der **`HectorServer.py`** ist das zentrale Hardware-Backend des Projekts.  
Er läuft auf dem **Raspberry Pi** und steuert alle angeschlossenen Komponenten über **GPIO** und **I²C**.

---

### 🧩 Aufgaben & Funktionen

| Bereich         | Beschreibung |
|-----------------|---------------|
| **Aktoren**     | Steuerung von Relais (Pumpe, Servos), Servos über PCA9685 |
| **Sensorik**    | Gewichtsmessung über HX711 |
| **Kommunikation** | MQTT-Schnittstelle für Befehle und Statusdaten |
| **Erweiterbarkeit** | Einfache Integration weiterer Sensoren und Aktoren |

---

### MQTT-Integration

Der Server nutzt **MQTT** zur Kommunikation mit dem Steuerungs-Frontend oder anderen Diensten.  
Er agiert als **Subscriber** (Befehle empfangen) und **Publisher** (Status senden).
