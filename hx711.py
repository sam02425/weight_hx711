import RPi.GPIO as GPIO
import time
import threading

class HX711:
    def __init__(self, dout_pin, pd_sck_pin, gain=128):
        self.PD_SCK = pd_sck_pin
        self.DOUT = dout_pin

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.PD_SCK, GPIO.OUT)
        GPIO.setup(self.DOUT, GPIO.IN)

        self.GAIN = 0
        self.REFERENCE_UNIT = 1
        self.OFFSET = 1
        self.lastVal = int(0)

        self.isNegative = False
        self.MSBIndex = 0
        self.LSBIndex = 0

        self.readLock = threading.Lock()

        self.set_gain(gain)

    def is_ready(self):
        return GPIO.input(self.DOUT) == 0

    def set_gain(self, gain):
        if gain == 128:
            self.GAIN = 1
        elif gain == 64:
            self.GAIN = 3
        elif gain == 32:
            self.GAIN = 2
        else:
            raise ValueError("Gain must be 128, 64, or 32")

        GPIO.output(self.PD_SCK, False)
        self.read()

    def read(self):
        with self.readLock:
            while not self.is_ready():
                pass

            value = 0
            for i in range(24):
                GPIO.output(self.PD_SCK, True)
                GPIO.output(self.PD_SCK, False)
                value = (value << 1) | GPIO.input(self.DOUT)

            for _ in range(self.GAIN):
                GPIO.output(self.PD_SCK, True)
                GPIO.output(self.PD_SCK, False)

            if value & 0x800000:  # negative flag is set
                value -= 1 << 24

            return value

    def get_value(self):
        return self.read() - self.OFFSET

    def get_weight(self, times=3):
        values = []
        for _ in range(times):
            values.append(self.get_value())
        return sum(values) / len(values) / self.REFERENCE_UNIT

    def tare(self, times=15):
        self.set_reference_unit(1)
        self.OFFSET = self.read_average(times)
        self.set_reference_unit(self.REFERENCE_UNIT)

    def set_reading_format(self, byte_format="MSB", bit_format="MSB"):
        if byte_format == "LSB":
            self.LSBIndex = 0
            self.MSBIndex = 2
        elif byte_format == "MSB":
            self.LSBIndex = 2
            self.MSBIndex = 0
        else:
            raise ValueError("Unrecognised byte_format: ", byte_format)

        if bit_format == "LSB":
            self.isNegative = lambda value: value & 0x80
        elif bit_format == "MSB":
            self.isNegative = lambda value: value & 0x1
        else:
            raise ValueError("Unrecognised bit_format: ", bit_format)

    def set_offset(self, offset):
        self.OFFSET = offset

    def set_reference_unit(self, reference_unit):
        self.REFERENCE_UNIT = reference_unit

    def power_down(self):
        GPIO.output(self.PD_SCK, False)
        GPIO.output(self.PD_SCK, True)
        time.sleep(0.0001)

    def power_up(self):
        GPIO.output(self.PD_SCK, False)
        time.sleep(0.0001)

    def reset(self):
        self.power_down()
        self.power_up()

    def read_average(self, times=3):
        values = []
        for _ in range(times):
            values.append(self.read())
        return sum(values) / len(values)

# Additional methods can be added as needed
