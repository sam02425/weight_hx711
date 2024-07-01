import time
import RPi.GPIO as GPIO
from hx711 import HX711
from utils import logger, get_stable_reading

class WeightSensor:
    def __init__(self, dout_pin=5, pd_sck_pin=6):
        self.hx = HX711(dout_pin, pd_sck_pin)
        self.hx.set_reading_format("MSB", "MSB")
        self.weight = 0
        self.reference_unit = 1
        self.dout_pin = dout_pin
        self.pd_sck_pin = pd_sck_pin
        logger.info(f"WeightSensor initialized with pins: DOUT={dout_pin}, PD_SCK={pd_sck_pin}")

    def setup(self):
        self.hx.reset()
        self.tare()
        logger.info("WeightSensor setup completed")

    def get_weight(self):
        try:
            if self.reference_unit == 0:
                raise ValueError("Reference unit is zero. Please calibrate the sensor.")
            raw_value = get_stable_reading(self.hx)
            self.weight = raw_value / self.reference_unit
            logger.debug(f"Current weight: {self.weight:.2f} g (Raw value: {raw_value})")
            return self.weight
        except Exception as e:
            logger.error(f"Error reading weight: {e}")
            return 0

    def tare(self):
        logger.info("Taring the scale...")
        self.hx.tare()
        logger.info("Tare completed")

    def set_reference_unit(self, reference_unit):
        if reference_unit == 0:
            logger.error("Cannot set reference unit to zero")
            return
        self.reference_unit = reference_unit
        self.hx.set_reference_unit(reference_unit)
        logger.info(f"Reference unit set to {reference_unit}")

    def read_raw_value(self):
        return self.hx.read()

    def check_connection(self):
        if GPIO.input(self.dout_pin) == 0:
            logger.info("HX711 DOUT pin is LOW (as expected when ready)")
            return True
        else:
            logger.warning("HX711 DOUT pin is HIGH (unexpected, might indicate a problem)")
            return False

    def cleanup(self):
        logger.info("Cleaning up GPIO")
        GPIO.cleanup()
