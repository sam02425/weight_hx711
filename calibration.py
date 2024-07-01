import time
import pickle
from weight_sensor import WeightSensor
from utils import logger
import RPi.GPIO as GPIO

def check_connection(sensor):
    logger.info("Checking HX711 connection...")
    if GPIO.input(sensor.hx.DOUT) == 0:
        logger.info("HX711 DOUT pin is LOW (as expected when ready)")
    else:
        logger.warning("HX711 DOUT pin is HIGH (unexpected, might indicate a problem)")

def read_raw_values(sensor, num_readings=20):
    logger.info(f"Reading {num_readings} raw values...")
    raw_values = []
    for i in range(num_readings):
        value = sensor.hx.read()
        raw_values.append(value)
        logger.debug(f"Raw reading {i+1}: {value}")
        time.sleep(0.1)
    return raw_values

def calibrate():
    sensor = WeightSensor()
    sensor.setup()

    check_connection(sensor)

    logger.info("Starting calibration process...")
    
    input("Please ensure the scale is empty, then press Enter to continue...")
    sensor.tare()
    logger.info("Tare completed")

    # Read some raw values after tare
    tare_values = read_raw_values(sensor)
    logger.info(f"Raw values after tare: {tare_values}")

    known_weight = float(input("Place a known weight on the scale and enter the weight in grams: "))
    
    # Read raw values with weight
    weight_values = read_raw_values(sensor)
    logger.info(f"Raw values with weight: {weight_values}")

    if all(v == 0 for v in weight_values):
        logger.error("All raw values are zero. Unable to calibrate.")
        logger.info("Please check your wiring and ensure the HX711 is properly connected.")
        return

    raw_value = sum(weight_values) / len(weight_values)
    logger.info(f"Average raw value: {raw_value}")

    if raw_value == 0:
        logger.error("Average raw value is zero. Unable to calibrate.")
        return
    
    reference_unit = raw_value / known_weight
    
    if reference_unit == 0:
        logger.error("Calculated reference unit is zero. Unable to calibrate.")
        return

    sensor.set_reference_unit(reference_unit)

    calibration_data = {'reference_unit': reference_unit}
    with open('calibration_data.pkl', 'wb') as f:
        pickle.dump(calibration_data, f)

    logger.info(f"Calibration complete. Reference unit: {reference_unit}")

    # Verify calibration
    measured_weight = sensor.get_weight()
    logger.info(f"Verification: Known weight: {known_weight}g, Measured weight: {measured_weight:.2f}g")

    sensor.cleanup()

if __name__ == "__main__":
    calibrate()
