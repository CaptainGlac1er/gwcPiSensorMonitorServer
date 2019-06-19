import time

from Adafruit_GPIO import SPI
from Adafruit_WS2801 import WS2801Pixels, RGB_to_color
import RPi.GPIO as GPIO


class LEDService:
    # Configure the count of pixels:
    PIXEL_COUNT = 1

    # Alternatively specify a hardware SPI connection on /dev/spidev0.0:
    SPI_PORT = 1
    SPI_DEVICE = 0

    def __init__(self):
        self.led = WS2801Pixels(self.PIXEL_COUNT, spi=SPI.SpiDev(self.SPI_PORT, self.SPI_DEVICE), gpio=GPIO)
        self.led.clear()
        self.led.show()

    def set_color(self, r, g, b):
        self.led.set_pixel(0, RGB_to_color(r, g, b))
        self.led.show()
        time.sleep(0.01)

    def get_led(self):
        return self.led
