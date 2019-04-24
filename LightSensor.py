import time
from GPIOService import GPIOService


class LightSensor:

    def __init__(self, gpio_service: GPIOService, pin):
        self.gpio_service = gpio_service
        self.pin = pin

    def get_data(self):
        count = 0
        self.gpio_service.set_pin_as(self.pin, GPIOService.OUT)
        self.gpio_service.output_pin(self.pin, GPIOService.LOW)
        time.sleep(.1)
        self.gpio_service.set_pin_as(self.pin, GPIOService.IN)
        while self.gpio_service.get_pin_status(self.pin) == GPIOService.LOW:
            count += 1
        return count
