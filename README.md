# Weight Sensing System for Raspberry Pi 4B

This project implements a weight sensing system using four HX711 load cell amplifiers connected to a Raspberry Pi 4B. The system includes calibration, weight prediction, and real-time operation capabilities.

## Hardware Requirements

- Raspberry Pi 4B
- 4x HX711 load cell amplifiers
- 4x Load cells (compatible with HX711)
- Breadboard and jumper wires

## Software Requirements

- Python 3.7+
- Required Python packages (see requirements.txt)

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/weight_sensing_system.git
   cd weight_sensing_system
   ```

2. Install required packages:
   ```
   pip install -r requirements.txt
   ```

3. Connect the HX711 sensors to the Raspberry Pi according to the following pin configuration:

   | HX711 | Raspberry Pi |
   |-------|--------------|
   | VCC   | 5V           |
   | GND   | GND          |
   | DT    | GPIO 5, 6, 13, 19 |
   | SCK   | GPIO 12, 16, 20, 26 |

   Note: Each HX711 uses a pair of DT and SCK pins.

## Usage

1. Calibrate the sensors:
   ```
   python calibration.py
   ```
   Follow the on-screen instructions to calibrate each sensor.

2. Run the real-time weight sensing system:
   ```
   python real_time_system.py
   ```

## File Descriptions

- `calibration.py`: Script for calibrating the HX711 sensors
- `weight_prediction.py`: Contains the weight prediction model
- `real_time_system.py`: Runs the real-time weight sensing system
- `utils.py`: Utility functions for sensor operations
- `config.py`: Configuration settings for the system

## Troubleshooting

If you encounter any issues, please check the following:
- Ensure all connections are secure and correct
- Verify that the correct GPIO pins are specified in `config.py`
- Check that all required packages are installed

For further assistance, please open an issue on the GitHub repository.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Additional Requirements

- Enable I2C and SPI interfaces on Raspberry Pi (use `raspi-config`)
- Ensure sufficient power supply for Raspberry Pi and all sensors
- Consider using a case or enclosure to protect the Raspberry Pi and sensors
- For production use, implement proper error handling and logging
- Consider adding a display (e.g., LCD) for real-time weight display without requiring a monitor

## Connection Instructions

1. Connect each HX711 module to its corresponding load cell following the manufacturer's instructions.
2. Connect the HX711 modules to the Raspberry Pi according to the pin configuration in the table above.
3. Ensure all ground (GND) connections are properly made.
4. Double-check all connections before powering on the Raspberry Pi.
5. For best results, use shielded cables for connections between load cells and HX711 modules, especially in noisy environments.

## Calibration Tips

- Use a range of known weights that cover the expected range of measurements
- Perform calibration in the same environmental conditions as the intended use
- Recalibrate periodically to maintain accuracy

## Maintenance

- Regularly check all connections for any signs of wear or looseness
- Keep the system clean and free from dust and debris
- Update the software regularly to ensure you have the latest features and bug fixes