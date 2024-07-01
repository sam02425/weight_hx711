import time
import RPi.GPIO as GPIO
from hx711 import HX711
import numpy as np
import pickle
from config import SENSOR_CONFIGS

def setup_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

def calibrate_sensor(dout_pin, pd_sck_pin):
    hx = HX711(dout_pin, pd_sck_pin)
    hx.set_reading_format("MSB", "MSB")
    hx.reset()
    hx.tare()

    input("Place a known weight on the scale and press Enter...")
    readings = []
    for _ in range(10):
        readings.append(hx.get_weight(5))
        time.sleep(0.1)

    measured_weight = np.mean(readings)
    actual_weight = float(input("Enter the actual weight in grams: "))

    calibration_factor = measured_weight / actual_weight
    return calibration_factor

def main():
    setup_gpio()
    calibration_data = {}

    for sensor_id, (dout_pin, pd_sck_pin) in SENSOR_CONFIGS.items():
        print(f"\nCalibrating sensor {sensor_id}...")
        calibration_factor = calibrate_sensor(dout_pin, pd_sck_pin)
        calibration_data[sensor_id] = calibration_factor
        print(f"Calibration factor for sensor {sensor_id}: {calibration_factor}")

    with open('calibration_data.pkl', 'wb') as f:
        pickle.dump(calibration_data, f)

    print("\nCalibration complete. Data saved to calibration_data.pkl")

if __name__ == "__main__":
    main()