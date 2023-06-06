import time

import smbus2


class I2CService:
    bus: smbus2.SMBus = None
    I2C_address = None

    def __init__(self, bus: smbus2.SMBus, i2c_address):
        self.I2C_address = i2c_address
        self.bus = bus

    def read_byte(self, adr):
        retry_times = 5
        while retry_times > 0:
            try:
                return self.bus.read_byte_data(self.I2C_address, adr)
            except OSError:
                retry_times = retry_times - 1
                time.sleep(1)
                continue

    def read_word(self, adr):
        retry_times = 5
        while retry_times > 0:
            try:
                high = self.bus.read_byte_data(self.I2C_address, adr)
                low = self.bus.read_byte_data(self.I2C_address, adr+1)
                val = (high << 8) + low
                return val
            except OSError:
                retry_times = retry_times - 1
                time.sleep(1)
                continue

    def read_word_2c(self, adr):
        val = self.read_word(adr)
        if val >= 0x8000:
            return -((65535 - val) + 1)
        else:
            return val

    def write_byte(self, adr, data):
        retry_times = 5
        while retry_times > 0:
            try:
                self.bus.write_byte_data(self.I2C_address, adr, data)
                return
            except OSError:
                retry_times = retry_times - 1
                time.sleep(1)
                continue

