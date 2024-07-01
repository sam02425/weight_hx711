import numpy as np
from scipy.optimize import curve_fit

import serial
import time
from utils import logger

class WeightPredictor:
    def __init__(self, port='/dev/ttyUSB0', baudrate=9600, timeout=1):
        try:
            self.ser = serial.Serial(port, baudrate, timeout=timeout)
            time.sleep(2)  # Allow time for sensor to initialize
            logger.info(f"Connected to weight sensor on {port}")
        except serial.SerialException as e:
            logger.error(f"Failed to connect to weight sensor: {e}")
            self.ser = None

    def predict(self, num_readings=3):
        if self.ser is None:
            logger.error("Weight sensor not initialized. Cannot predict weight.")
            return 0

        weights = []
        for _ in range(num_readings):
            try:
                self.ser.write(b'R\r\n')  # Send command to request weight
                response = self.ser.readline().decode('utf-8').strip()
                weight = float(response)
                weights.append(weight)
            except ValueError:
                logger.warning(f"Invalid weight reading: {response}")
            except serial.SerialException as e:
                logger.error(f"Error communicating with weight sensor: {e}")
                return 0

        if weights:
            return sum(weights) / len(weights)
        else:
            return 0

    def tare(self):
        if self.ser is None:
            logger.error("Weight sensor not initialized. Cannot tare.")
            return False

        try:
            self.ser.write(b'T\r\n')  # Send tare command
            response = self.ser.readline().decode('utf-8').strip()
            if response == 'OK':
                logger.info("Tare successful")
                return True
            else:
                logger.warning(f"Tare failed: {response}")
                return False
        except serial.SerialException as e:
            logger.error(f"Error communicating with weight sensor: {e}")
            return False

    def close(self):
        if self.ser:
            self.ser.close()
            logger.info("Closed connection to weight sensor")

def main():
    predictor = WeightPredictor()
    try:
        if predictor.tare():
            for _ in range(5):
                weight = predictor.predict()
                print(f"Current weight: {weight:.2f} g")
                time.sleep(1)
    finally:
        predictor.close()

if __name__ == "__main__":
    main()
