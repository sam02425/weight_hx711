import RPi.GPIO as GPIO
import time
import numpy as np
import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    logger = logging.getLogger('weight_sensing_system')
    logger.setLevel(logging.DEBUG)
    handler = RotatingFileHandler('weight_sensing_system.log', maxBytes=10000000, backupCount=5)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

logger = setup_logging()

def setup_gpio():
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        logger.info("GPIO setup completed")
    except Exception as e:
        logger.error(f"Error setting up GPIO: {e}")
        raise

def get_stable_reading(hx, num_readings=10, delay=0.1):
    readings = []
    try:
        for _ in range(num_readings):
            readings.append(hx.get_weight(5))
            time.sleep(delay)
        stable_reading = np.median(readings)
        logger.debug(f"Stable reading: {stable_reading}")
        return stable_reading
    except Exception as e:
        logger.error(f"Error getting stable reading: {e}")
        raise

def graceful_shutdown():
    logger.info("Initiating graceful shutdown")
    GPIO.cleanup()
    logger.info("GPIO cleanup completed")