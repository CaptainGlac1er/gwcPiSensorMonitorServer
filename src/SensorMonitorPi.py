#!/usr/bin/python
import getopt
import sys

import smbus2
import time
import threading
import json
from datetime import datetime, date

from TemperatureSensor import TemperatureSensor
from I2CService import I2CService
from LCDService import LCDService
from LEDService import LEDService
from MotionSensor import MotionSensor
from LightSensor import LightSensor
from GPIOService import GPIOService
from Server import Server


gather_event = threading.Event()

def check_light(light_sensor_connection: LightSensor, lcd_service: LCDService, led_service: LEDService, output):
    print("starting light")
    while not gather_event.is_set():

        light_level = light_sensor_connection.get_data()
        # print("light sensor")
        # print("---------")
        # print("sensor: %5d" % (light_level))
        normized = (50000 - light_level) / 50000
        led_service.set_color(round(255 * normized), round(255 * (1 - normized)), 0)
        lcd_service.write_line('{:d}'.format(light_level))
        output({
            "light": light_level
        })
        time.sleep(10)


def check_bme680(bme680_sensor_connection: TemperatureSensor, output):
    print("starting bme")
    while not gather_event.is_set():
        data = bme680_sensor_connection.get_data()
        if data:
            output(data)
        time.sleep(10)


def check_gyro(motion_sensor_connection: MotionSensor, output):
    print("starting gyro")
    while not gather_event.is_set():

        gyro = motion_sensor_connection.get_gyro()

        accel = motion_sensor_connection.get_acceleration()

        accel_xout_scaled = accel[0] / 16384.0
        accel_yout_scaled = accel[1] / 16384.0
        accel_zout_scaled = accel[2] / 16384.0

        x_rotation = motion_sensor_connection.get_x_rotation(accel_xout_scaled, accel_yout_scaled, accel_zout_scaled)
        y_rotation = motion_sensor_connection.get_y_rotation(accel_xout_scaled, accel_yout_scaled, accel_zout_scaled)

        temp = motion_sensor_connection.get_temp()
        output({
            "gyro": {
                "x": gyro[0],
                "y": gyro[1],
                "z": gyro[2]
            },
            "accelerometer": {
                "x": accel_xout_scaled,
                "y": accel_yout_scaled,
                "z": accel_zout_scaled,
            }
        })
        # print("temp: ", temp)
        time.sleep(.500)

def main(argv):
    optlist, args = getopt.getopt(argv, '', ['output-folder='])
    folder = None
    for option, argument in optlist:
        if option == "--output-folder":
            folder = argument
    if folder is None:
        exit(1)
    bme680_file = f'{folder}/bme680-{date.today()}.csv'
    bus = smbus2.SMBus(1)  # or bus = smbus.SMBus(1) for Revision 2 boards
    time.sleep(1)
    address = 0x68  # This is the address value read via the i2cdetect command
    lcd_service = LCDService()
    lcd_service.write_line("Hello")
    led_service = LEDService()
    bme_sensor = TemperatureSensor()
    motion_sensor = MotionSensor(I2CService(bus, address), 0)
    test = motion_sensor.start_up_gyro()

    gpio_service = GPIOService()
    light_sensor = LightSensor()
    buffer_filo = []

    server = Server(2048)

    def save_data(file_name, printer, send_data):
        def handle(data):
            with open(file_name, "a") as output_file:
                send_data(data)
                data_line = printer(data)
                output_file.write(data_line)
                output_file.write("\n")

        return handle

    def send_data(data):
        data_string = json.dumps(data)
        server.send_data(data_string)

    def format_light_sensor(data):
        return f'{datetime.utcnow()},' \
               f'{data["light"]}'

    def format_gyro(data):
        return f'{datetime.utcnow()},' \
               f'{data["gyro"]["x"]},{data["gyro"]["y"]},{data["gyro"]["z"]},' \
               f'{data["accelerometer"]["x"]},{data["accelerometer"]["y"]},{data["accelerometer"]["z"]}'

    def format_bme(data):
        return f'{data["bme680"]["timestamp"]},' \
               f'{data["bme680"]["temperature"]},{data["bme680"]["gas"]},{data["bme680"]["humidity"]},' \
               f'{data["bme680"]["pressure"]},{data["bme680"]["altitude"]}'

    light_thread = threading.Thread(
        target=check_light,
        args=(light_sensor,
              lcd_service,
              led_service,
              save_data(
                  f'{folder}/light-thread-{date.today()}.csv',
                  format_light_sensor,
                  send_data)
              )
    )
    gyro_thread = threading.Thread(
        target=check_gyro,
        args=(motion_sensor,
              save_data(f'{folder}/motion-sensor-{date.today()}.csv',
                        format_gyro,
                        send_data
                        )
              )
    )
    bme_thread = threading.Thread(
        target=check_bme680,
        args=(bme_sensor,
              save_data(f'{folder}/bme680-{date.today()}.csv',
                        format_bme,
                        send_data
                        )
              )
    )
    try:
        gather_event.clear()
        server.start()
        light_thread.start()
        bme_thread.start()
        gyro_thread.start()
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        print("\nStopping Server")
        gather_event.set()
        server.stop()
        sys.exit()


if __name__ == '__main__':
    main(sys.argv[1:])
