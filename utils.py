import time
import RPi.GPIO as GPIO
import logging

def setup_logging():
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    return logging.getLogger('weight_sensing_system')

logger = setup_logging()

def setup_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

def get_stable_reading(hx, num_readings=10, delay=0.1):
    readings = []
    for _ in range(num_readings):
        try:
            value = hx.get_weight(5)
            if value != 0:  # Avoid adding zero readings
                readings.append(value)
        except Exception as e:
            logger.error(f"Error in individual reading: {e}")
        time.sleep(delay)
    
    if not readings:
        logger.warning("No valid readings obtained")
        return 0
    
    return sum(readings) / len(readings)

def graceful_shutdown():
    GPIO.cleanup()
    logger.info("GPIO cleaned up")
