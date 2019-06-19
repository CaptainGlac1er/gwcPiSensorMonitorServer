import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn


class LightSensor:

    def __init__(self):
        i2c = busio.I2C(board.SCL, board.SDA)
        self.ads = ADS.ADS1115(i2c)
        self.channel = AnalogIn(self.ads, ADS.P0)
        self.channel2 = AnalogIn(self.ads, ADS.P1)

    def get_data(self):
        print("pod: {:d}".format(self.channel2.value))
        return self.channel.value
