class I2CService:
    bus = None
    I2C_address = None

    def __init__(self, bus, i2c_address):
        self.I2C_address = i2c_address
        self.bus = bus

    def read_byte(self, adr):
        return self.bus.read_byte_data(self.I2C_address, adr)

    def read_word(self, adr):
        high = self.bus.read_byte_data(self.I2C_address, adr)
        low = self.bus.read_byte_data(self.I2C_address, adr+1)
        val = (high << 8) + low
        return val

    def read_word_2c(self, adr):
        val = self.read_word(adr)
        if val >= 0x8000:
            return -((65535 - val) + 1)
        else:
            return val

    def write_byte(self, adr, data):
        self.bus.write_byte_data(self.I2C_address, adr, data)

