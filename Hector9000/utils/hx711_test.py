from Hector9000.conf.hx711 import HX711
import time

# Pins aus HectorConfig.py (physikalische Pins, also BOARD-Nummerierung)
# DT = 31, SCK = 29
hx = HX711(dout=31, pd_sck=29)
hx.set_reference_unit(100)  # Kalibrierwert anpassen falls nötig

hx.reset()
hx.tare()
print("Waage tariert. Bitte nichts auflegen.")

time.sleep(2)
print("Jetzt bitte etwas auflegen...")

while True:
    gewicht = float(hx.get_weight(5))
    print(f"Aktuelles Gewicht: {gewicht:.2f} g")
    hx.power_down()
    hx.power_up()
    time.sleep(1)
