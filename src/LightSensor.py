import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn


class LightSensor:

    def __init__(self):
        i2c = busio.I2C(board.SCL, board.SDA)
        self.ads = ADS.ADS1115(i2c)
        self.channel = AnalogIn(self.ads, ADS.P0)

    def get_data(self):
        return self.channel.value
