import time
import RPi.GPIO as GPIO
from hx711 import HX711
from utils import logger

class WeightPredictor:
    def __init__(self, dout_pin=5, pd_sck_pin=6, reference_unit=1):
        self.dout_pin = dout_pin
        self.pd_sck_pin = pd_sck_pin
        self.reference_unit = reference_unit
        self.hx = None
        self.setup_gpio()
        self.setup_hx711()

    def setup_gpio(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

    def setup_hx711(self):
        try:
            self.hx = HX711(self.dout_pin, self.pd_sck_pin)
            self.hx.set_reading_format("MSB", "MSB")
            self.hx.set_reference_unit(self.reference_unit)
            self.hx.reset()
            self.hx.tare()
            logger.info("HX711 initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize HX711: {e}")
            self.hx = None

    def predict(self, num_readings=5):
        if self.hx is None:
            logger.error("HX711 not initialized. Cannot predict weight.")
            return 0

        weights = []
        for _ in range(num_readings):
            try:
                weight = self.hx.get_weight(5)
                self.hx.power_down()
                self.hx.power_up()
                weights.append(weight)
                time.sleep(0.1)
            except Exception as e:
                logger.error(f"Error reading weight: {e}")

        if weights:
            average_weight = sum(weights) / len(weights)
            logger.debug(f"Average weight reading: {average_weight}")
            return average_weight
        else:
            logger.warning("No valid weight readings obtained")
            return 0

    def tare(self):
        if self.hx is None:
            logger.error("HX711 not initialized. Cannot tare.")
            return False

        try:
            self.hx.tare()
            logger.info("Tare completed successfully")
            return True
        except Exception as e:
            logger.error(f"Error during tare operation: {e}")
            return False

    def set_reference_unit(self, reference_unit):
        if self.hx is None:
            logger.error("HX711 not initialized. Cannot set reference unit.")
            return

        try:
            self.reference_unit = reference_unit
            self.hx.set_reference_unit(reference_unit)
            logger.info(f"Reference unit set to {reference_unit}")
        except Exception as e:
            logger.error(f"Error setting reference unit: {e}")

    def calibrate(self, known_weight):
        if self.hx is None:
            logger.error("HX711 not initialized. Cannot calibrate.")
            return

        try:
            logger.info("Starting calibration. Please ensure the scale is empty.")
            input("Press Enter when ready...")
            self.tare()

            logger.info(f"Please place a known weight of {known_weight} units on the scale.")
            input("Press Enter when ready...")

            reading = self.hx.get_weight(20)
            self.hx.power_down()
            self.hx.power_up()

            actual_reference_unit = reading / known_weight
            self.set_reference_unit(actual_reference_unit)

            logger.info(f"Calibration complete. Reference unit set to {actual_reference_unit}")
        except Exception as e:
            logger.error(f"Error during calibration: {e}")

    def close(self):
        if self.hx:
            GPIO.cleanup()
            logger.info("Cleaned up GPIO")

def main():
    try:
        predictor = WeightPredictor()
        
        # Calibration
        known_weight = float(input("Enter the weight of your calibration object (in grams): "))
        predictor.calibrate(known_weight)

        # Test readings
        for _ in range(5):
            weight = predictor.predict()
            print(f"Current weight: {weight:.2f} g")
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nProgram terminated by user")
    finally:
        if predictor:
            predictor.close()

if __name__ == "__main__":
    main()
