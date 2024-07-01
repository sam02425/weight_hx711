import time
import RPi.GPIO as GPIO
from hx711 import HX711
import numpy as np
import pickle
from config import SENSOR_CONFIGS, DATA_SAVE_INTERVAL, DATA_FILE, WEB_SERVER_PORT
from weight_prediction import WeightPredictor
from utils import setup_gpio, get_stable_reading, logger, graceful_shutdown
import threading
import csv
from http.server import BaseHTTPRequestHandler, HTTPServer
import json

class SensorReader(threading.Thread):
    def __init__(self, sensor_id, hx):
        threading.Thread.__init__(self)
        self.sensor_id = sensor_id
        self.hx = hx
        self.weight = 0
        self.running = True

    def run(self):
        while self.running:
            try:
                self.weight = get_stable_reading(self.hx)
                logger.debug(f"Sensor {self.sensor_id}: {self.weight:.2f} g")
                time.sleep(0.1)
            except Exception as e:
                logger.error(f"Error reading sensor {self.sensor_id}: {e}")

    def stop(self):
        self.running = False

class DataSaver(threading.Thread):
    def __init__(self, sensors, predictor):
        threading.Thread.__init__(self)
        self.sensors = sensors
        self.predictor = predictor
        self.running = True

    def run(self):
        while self.running:
            try:
                sensor_readings = [sensor.weight for sensor in self.sensors.values()]
                predicted_weight = self.predictor.predict(np.array(sensor_readings))
                self.save_data(sensor_readings, predicted_weight)
                time.sleep(DATA_SAVE_INTERVAL)
            except Exception as e:
                logger.error(f"Error saving data: {e}")

    def save_data(self, sensor_readings, predicted_weight):
        with open(DATA_FILE, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([time.time()] + sensor_readings + [predicted_weight])
        logger.info("Data saved successfully")

    def stop(self):
        self.running = False

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def __init__(self, sensors, predictor, *args, **kwargs):
        self.sensors = sensors
        self.predictor = predictor
        super().__init__(*args, **kwargs)

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        sensor_readings = [sensor.weight for sensor in self.sensors.values()]
        predicted_weight = self.predictor.predict(np.array(sensor_readings))
        data = {
            'sensor_readings': sensor_readings,
            'predicted_weight': predicted_weight
        }
        self.wfile.write(json.dumps(data).encode())

def start_web_server(sensors, predictor):
    def handler(*args):
        SimpleHTTPRequestHandler(sensors, predictor, *args)
    server = HTTPServer(('', WEB_SERVER_PORT), handler)
    logger.info(f"Started web server on port {WEB_SERVER_PORT}")
    server.serve_forever()

def main():
    try:
        setup_gpio()

        # Load calibration data
        with open('calibration_data.pkl', 'rb') as f:
            calibration_data = pickle.load(f)

        # Initialize sensors and start sensor reading threads
        sensors = {}
        sensor_threads = {}
        for sensor_id, (dout_pin, pd_sck_pin) in SENSOR_CONFIGS.items():
            hx = HX711(dout_pin, pd_sck_pin)
            hx.set_reading_format("MSB", "MSB")
            hx.set_reference_unit(calibration_data[sensor_id])
            hx.reset()
            hx.tare()
            sensors[sensor_id] = hx
            sensor_thread = SensorReader(sensor_id, hx)
            sensor_thread.start()
            sensor_threads[sensor_id] = sensor_thread

        # Load weight prediction model
        predictor = WeightPredictor()
        predictor.load_model('weight_model.npy')

        # Start data saver thread
        data_saver = DataSaver(sensor_threads, predictor)
        data_saver.start()

        # Start web server in a separate thread
        web_server_thread = threading.Thread(target=start_web_server, args=(sensor_threads, predictor))
        web_server_thread.start()

        logger.info("Real-time weight sensing system started")

        while True:
            sensor_readings = [sensor_thread.weight for sensor_thread in sensor_threads.values()]
            predicted_weight = predictor.predict(np.array(sensor_readings))
            logger.info(f"Predicted total weight: {predicted_weight:.2f} g")
            time.sleep(1)

    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received. Shutting down...")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        for sensor_thread in sensor_threads.values():
            sensor_thread.stop()
        data_saver.stop()
        graceful_shutdown()

if __name__ == "__main__":
    main()