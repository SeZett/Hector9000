## **Hardwaresteuerung**

| Topic | Nachricht (Payload) | Beschreibung |
|-------|----------------------|---------------|
| `Hector9000/Hardware/pump_start` | `True` | Schaltet die Förderpumpe ein |
| `Hector9000/Hardware/pump_stop` | `True` | Schaltet die Förderpumpe aus |
| `Hector9000/Hardware/servo/<channel>` | `0.0–1.0` | Steuert den Servo am angegebenen Kanal (0–15) |
| `Hector9000/Hardware/relay/<id>` | `True`/`False` | Schaltet ein bestimmtes Relais (z. B. Servoversorgung) |
| `Hector9000/Hardware/reset` | – | Setzt alle Ausgänge in Grundzustand |

---

## **Sensorik**

| Topic | Payload | Beschreibung |
|--------|----------|--------------|
| `Hector9000/Sensor/weight` | Zahl (g) | Aktuelles Gewicht von der HX711 |
| `Hector9000/Sensor/ready` | `True`/`False` | Gibt an, ob Sensorwerte verfügbar sind |
| `Hector9000/Sensor/calibrate` | `True` | Startet Kalibrierung der Waage |

---

##  **Status & Rückmeldungen**

| Topic | Payload | Beschreibung |
|--------|----------|--------------|
| `Hector9000/Status/connected` | `True`/`False` | Gibt Verbindungsstatus des Servers aus |
| `Hector9000/Status/heartbeat` | Zahl (Sekunden) | Periodisches Lebenszeichen |
| `Hector9000/Status/error` | Text | Gibt Fehlermeldungen aus |
| `Hector9000/LEDStrip/standard` | `R,G,B,Helligkeit` | (Optional) LED-Statusmeldung |

---

## 📘 **Beispiel-Workflow**

```bash
# Pumpe aktivieren
mosquitto_pub -h localhost -t 'Hector9000/Hardware/pump_start' -m 'True'

# Servo auf 50%
mosquitto_pub -h localhost -t 'Hector9000/Hardware/servo/0' -m '0.5'

# Gewicht abfragen
mosquitto_sub -h localhost -t 'Hector9000/Sensor/weight'
