import RPi.GPIO as GPIO
import time
import threading

class HX711:
    def __init__(self, dout, pd_sck, gain=128):
        self.PD_SCK = pd_sck
        self.DOUT = dout

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.PD_SCK, GPIO.OUT)
        GPIO.setup(self.DOUT, GPIO.IN)

        self.GAIN = 0
        self.REFERENCE_UNIT = 1
        self.REFERENCE_UNIT_B = 1
        self.OFFSET = 1
        self.OFFSET_B = 1
        self.lastVal = int(0)

        self.isNegative = False
        self.MSBIndex = 0
        self.LSBIndex = 0

        self.set_gain(gain)

        self.CLOCK_PIN = self.PD_SCK
        self.DATA_PIN = self.DOUT

        threading.Thread.__init__(self)
        self.daemon = True
        self.readLock = threading.Lock()

    def is_ready(self):
        return GPIO.input(self.DOUT) == 0

    def set_gain(self, gain):
        if gain is 128:
            self.GAIN = 1
        elif gain is 64:
            self.GAIN = 3
        elif gain is 32:
            self.GAIN = 2

        GPIO.output(self.PD_SCK, False)
        self.read()

    def createBoolList(self, size=8):
        ret = []
        for i in range(size):
            ret.append(False)
        return ret

    def read(self):
        self.readLock.acquire()
        value = 0

        while not self.is_ready():
            time.sleep(0.001)

        for i in range(24):
            GPIO.output(self.PD_SCK, True)
            GPIO.output(self.PD_SCK, False)
            value = (value << 1) | GPIO.input(self.DOUT)

        for i in range(self.GAIN):
            GPIO.output(self.PD_SCK, True)
            GPIO.output(self.PD_SCK, False)

        if (value & 0x800000):  # negative flag is set
            value = value - (1 << 24)

        self.readLock.release()

        return value

    def get_value(self):
        return self.read() - self.OFFSET

    def get_weight(self, times=3):
        value = self.get_value_B(times)
        value = value / self.REFERENCE_UNIT
        return value

    def tare(self, times=15):
        reference_unit = self.REFERENCE_UNIT
        self.set_reference_unit(1)

        value = self.read_average(times)
        self.set_offset(value)

        self.set_reference_unit(reference_unit)

    def set_reading_format(self, byte_format="LSB", bit_format="MSB"):
        if byte_format == "LSB":
            self.LSBIndex = 0
            self.MSBIndex = 2
        elif byte_format == "MSB":
            self.LSBIndex = 2
            self.MSBIndex = 0
        else:
            raise ValueError("Unrecognised byte_format: ", byte_format)

        if bit_format == "LSB":
            self.LSBIndex = 0
            self.MSBIndex = 2
        elif bit_format == "MSB":
            self.LSBIndex = 2
            self.MSBIndex = 0
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
        values = 0
        for i in range(times):
            values += self.read()

        return values / times

    def get_value_A(self):
        return self.get_value()

    def get_value_B(self, times=3):
        return self.read_average(times) - self.OFFSET

    def get_weight_A(self):
        return self.get_weight()

    def get_weight_B(self, times=3):
        value = self.get_value_B(times)
        value = value / self.REFERENCE_UNIT_B
        return value

    def set_offset_A(self, offset):
        self.set_offset(offset)

    def set_reference_unit_A(self, reference_unit):
        self.set_reference_unit(reference_unit)

    def set_offset_B(self, offset):
        self.OFFSET_B = offset

    def set_reference_unit_B(self, reference_unit):
        self.REFERENCE_UNIT_B = reference_unit

    def tare_A(self):
        self.tare()

    def tare_B(self):
        tare_B_times = 15
        reference_unit_B = self.REFERENCE_UNIT_B
        self.set_reference_unit_B(1)

        value = self.read_average(tare_B_times)
        self.set_offset_B(value)

        self.set_reference_unit_B(reference_unit_B)