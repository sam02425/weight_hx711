import time
import pickle
from config import DATA_SAVE_INTERVAL, DATA_FILE, WEB_SERVER_PORT
from utils import setup_gpio, logger, graceful_shutdown
from weight_sensor import WeightSensor
import threading
import csv
from http.server import BaseHTTPRequestHandler, HTTPServer
import json

# ... (keep the DataSaver and SimpleHTTPRequestHandler classes as they were) ...

def main():
    try:
        setup_gpio()
        logger.info("GPIO setup completed")

        weight_sensor = WeightSensor(dout_pin=5, pd_sck_pin=6)
        weight_sensor.setup()

        try:
            with open('calibration_data.pkl', 'rb') as f:
                calibration_data = pickle.load(f)
            reference_unit = calibration_data['reference_unit']
            if reference_unit == 0:
                raise ValueError("Invalid reference unit in calibration data")
            weight_sensor.set_reference_unit(reference_unit)
            logger.info(f"Calibration data loaded successfully. Reference unit: {reference_unit}")
        except (FileNotFoundError, KeyError, ValueError) as e:
            logger.error(f"Error loading calibration data: {e}")
            logger.warning("Please run the calibration process before using the system.")
            return

        data_saver = DataSaver(weight_sensor)
        data_saver.start()

        web_server_thread = threading.Thread(target=start_web_server, args=(weight_sensor,))
        web_server_thread.daemon = True
        web_server_thread.start()

        logger.info("Real-time weight sensing system started")

        while True:
            weight = weight_sensor.get_weight()
            logger.info(f"Current weight: {weight:.2f} g")
            time.sleep(1)

    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received. Shutting down...")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        if 'data_saver' in locals():
            data_saver.stop()
        if 'weight_sensor' in locals():
            weight_sensor.cleanup()
        graceful_shutdown()

if __name__ == "__main__":
    main()
