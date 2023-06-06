from RPLCD.gpio import CharLCD
from RPi import GPIO


class LCDService:
    def __init__(self):
        self.lcd = CharLCD(pin_rs=22,
                           pin_rw=24,
                           pin_e=23,
                           pins_data=[9, 25, 11, 24],
                           numbering_mode=GPIO.BCM,
                           cols=16,
                           rows=2,
                           dotsize=8,
                           charmap='A02',
                           auto_linebreaks=True)

    def write_line(self, text):
        self.lcd.clear()
        self.lcd.home()
        self.lcd.write_string(text)
