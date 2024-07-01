# GPIO pin configurations for each HX711 sensor
SENSOR_CONFIGS = {
    1: (5, 12),   # (DT, SCK)
    2: (6, 16),
    3: (13, 20),
    4: (19, 26)
}

# Data persistence configuration
DATA_SAVE_INTERVAL = 300  # Save data every 5 minutes
DATA_FILE = 'sensor_data.csv'

# Remote monitoring configuration
WEB_SERVER_PORT = 8080