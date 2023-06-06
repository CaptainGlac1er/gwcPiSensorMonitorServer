import time
from datetime import datetime
from typing import Union

import board
import busio
from adafruit_bme680 import Adafruit_BME680_I2C


class TemperatureSensor:

    def __init__(self):
        i2c = busio.I2C(board.SCL, board.SDA)
        self.bme680 = Adafruit_BME680_I2C(i2c, debug=False)
        print("initializing BME680")

    def get_data(self) -> Union[dict[str, Union[float, int]], None]:
        data = None
        try:
            data = {
                "bme680": {
                    "timestamp": datetime.utcnow().isoformat(),
                    "temperature": self.bme680.temperature,
                    "gas": self.bme680.gas,
                    "humidity": self.bme680.humidity,
                    "pressure": self.bme680.pressure,
                    "altitude": self.bme680.altitude,
                }
            }
        finally:
            return data
