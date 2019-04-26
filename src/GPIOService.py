import RPi.GPIO as GPIO


class GPIOService:
    LOW = GPIO.LOW
    HIGH = GPIO.HIGH

    OUT = GPIO.OUT
    IN = GPIO.IN

    def __init__(self):
        GPIO.setmode(GPIO.BCM)

    def set_pin_as(self, pin, status):
        GPIO.setup(pin, status)

    def output_pin(self, pin, status):
        GPIO.output(pin, status)

    def get_pin_status(self, pin):
        return GPIO.input(pin)
