#!/usr/bin/env python3
# -*- coding: utf8 -*-
##
#   HectorHardware.py       API class for Hector9000 hardware
##

from __future__ import division
import time
import sys
import threading
import logging

from Hector9000.utils import HectorAPI as api
from Hector9000.conf import HectorConfig
import Adafruit_PCA9685
import RPi.GPIO as GPIO
from Hector9000.conf.hx711 import HX711

# ====================================
# Logging
# ====================================
logging.basicConfig(level=logging.CRITICAL)
VERBOSE_LEVEL = 0


def log(message):
    if VERBOSE_LEVEL == 0:
        logging.log(VERBOSE_LEVEL, str(message))


def error(message):
    if VERBOSE_LEVEL < 3:
        print(f"Hardware ERROR: {message}")


def warning(message):
    if VERBOSE_LEVEL < 2:
        print(f"Hardware WARNING: {message}")


# ====================================
# Klasse HectorHardware
# ====================================
class HectorHardware(api.HectorAPI):

    def __init__(self, cfg, mqtt_client=None):
        print("[INIT] HectorHardware wird initialisiert...")
        log("initialization HectorHardware")

        self.config = cfg
        self.mqtt_client = mqtt_client
        GPIO.setmode(GPIO.BOARD)

        # ----------------------------
        # HX711 (Waage)
        # ----------------------------
        hx1 = cfg["hx711"]["CLK"]
        hx2 = cfg["hx711"]["DAT"]
        hxref = cfg["hx711"]["ref"]
        self.hx = HX711(hx1, hx2)
        self.hx.set_reading_format("LSB", "MSB")
        self.hx.set_reference_unit(hxref)
        self.hx.reset()
        self.hx.tare()
        log("HX711 Waage initialisiert und tariert.")

        # Starte Waage-Thread
        self._weight_thread_running = True
        self._weight_thread = threading.Thread(target=self._weight_loop, daemon=True)
        self._weight_thread.start()

        # ----------------------------
        # PCA9685 (Servosteuerung)
        # ----------------------------
        self.valveChannels = self.config["pca9685"]["valvechannels"]
        self.numValves = len(self.valveChannels)
        self.valvePositions = cfg["pca9685"]["valvepositions"]
        pcafreq = cfg["pca9685"]["freq"]

        self.pca = Adafruit_PCA9685.PCA9685()
        self.pca.set_pwm_freq(pcafreq)

        # ----------------------------
        # Relais / Pumpe
        # ----------------------------
        self.pump = cfg["pump"]["MOTOR"]
        GPIO.setup(self.pump, GPIO.IN)

    # --------------------------------
    # Grundfunktionen
    # --------------------------------
    def getConfig(self):
        return self.config

    def light_on(self):
        pass

    def light_off(self):
        pass

    def arm_out(self, cback=None):
        pass

    def arm_in(self, cback=None):
        pass

    def arm_isInOutPos(self):
        pass

    # --------------------------------
    # Waage
    # --------------------------------
    def scale_readout(self):
        weight = self.hx.get_weight(5)
        return weight

    def scale_tare(self):
        log("scale tare")
        self.hx.tare()

    # --------------------------------
    # Pumpe
    # --------------------------------
    def pump_start(self):
        log("start pump")
        GPIO.setup(self.pump, GPIO.OUT)

    def pump_stop(self):
        log("stop pump")
        GPIO.setup(self.pump, GPIO.IN)

    # --------------------------------
    # Ventile
    # --------------------------------
    def valve_open(self, index, open=1):
        if open == 0:
            log("close valve")
        else:
            log("open valve")

        if index < 0 or index >= len(self.valveChannels):
            return

        ch = self.valveChannels[index]
        pos = self.valvePositions[index][1 - open]
        log(f"ch {ch}, pos {pos}")
        self.pca.set_pwm(ch, 0, pos)

    def valve_close(self, index):
        log("close valve")
        self.valve_open(index, open=0)

    # --------------------------------
    # Dosieren
    # --------------------------------
    def valve_dose(self, index, amount, timeout=30, cback=None, progress=(0, 100), topic=""):
        log(f"dose channel {index}, amount {amount}")
        if index < 0 or index >= len(self.valveChannels):
            return -1
        if not self.arm_isInOutPos():
            return -1

        t0 = time.time()
        balance = True
        self.scale_tare()
        self.pump_start()
        self.valve_open(index)

        sr = float(self.scale_readout())
        if sr < -10:
            amount += sr
            balance = False

        last_over = False
        last = sr
        while True:
            sr = float(self.scale_readout())
            if balance and sr < -10:
                warning("weight abnormality: scale balanced")
                amount += sr
                balance = False
            if sr > amount:
                if last_over:
                    log("dosing complete")
                    break
                else:
                    last_over = True
            else:
                last_over = False
            log(f"Read scale: {sr}")

            if (sr - last) > 5:
                log("reset timeout")
                t0 = time.time()
                last = sr
            if (time.time() - t0) > timeout:
                error("timeout reached")
                self.pump_stop()
                self.valve_close(index)
                if cback:
                    cback(progress[0] + progress[1])
                return False

            time.sleep(0.1)

        self.pump_stop()
        self.valve_close(index)
        if cback:
            cback(progress[0] + progress[1])
        log("completed reset after dosing")
        return True

    # --------------------------------
    # Sonstige
    # --------------------------------
    def finger(self, pos=0):
        pass

    def ping(self, num, retract=True, cback=None):
        pass

    def cleanAndExit(self):
        log("Cleaning...")
        GPIO.cleanup()
        log("Bye!")
        sys.exit()

    # --------------------------------
    # Hilfsfunktion: Servo-Puls
    # --------------------------------
    def set_servo_pulse(self, channel, pulse):
        pulse_length = 1000000
        pulse_length //= 60
        log(f'{pulse_length} µs per period')
        pulse_length //= 4096
        log(f'{pulse_length} µs per bit')
        pulse *= 1000
        pulse //= pulse_length
        self.pca.set_pwm(channel, 0, pulse)

    # --------------------------------
    # HX711-Thread
    # --------------------------------
    def _weight_loop(self):
        """Kontinuierliche Messung der Waage und Publikation über MQTT"""
        topic = "Hector9000/Hardware/weight"
        while self._weight_thread_running:
            try:
                gewicht = float(self.hx.get_weight(5))
                if self.mqtt_client:
                    self.mqtt_client.publish(topic, str(gewicht))
                    print(f"[HX711-Thread] Gewicht publiziert: {gewicht:.2f} g")
            except Exception as e:
                warning(f"[HX711-Thread] Fehler: {e}")
            time.sleep(1)

    def stop_weight_thread(self):
        """Stoppt den Waage-Thread"""
        self._weight_thread_running = False
        self._weight_thread.join()
