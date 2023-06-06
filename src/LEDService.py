import time

import adafruit_ws2801
import board
from Adafruit_GPIO import SPI
from Adafruit_WS2801 import WS2801Pixels, RGB_to_color
import RPi.GPIO as GPIO


class LEDService:
    # Configure the count of pixels:
    PIXEL_COUNT = 1

    # Alternatively specify a hardware SPI connection on /dev/spidev0.0:
    SPI_PORT = 0
    SPI_DEVICE = 1

    def __init__(self):
        self.led = adafruit_ws2801.WS2801(board.SCLK_1, board.MOSI_1, self.PIXEL_COUNT)
        self.led.fill((0, 0, 0))
        self.led.brightness = 42
        self.led.show()

    def set_color(self, r, g, b):
        self.led[0] = (r, g, b)
        self.led.show()
        time.sleep(1)

    def get_led(self):
        return self.led
