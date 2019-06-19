#!/usr/bin/python

import smbus2
import time
import threading
import json
from datetime import datetime

from src.TemperatureSensor import TemperatureSensor
from src.I2CService import I2CService
from src.LCDService import LCDService
from src.LEDService import LEDService
from src.MotionSensor import MotionSensor
from src.LightSensor import LightSensor
from src.GPIOService import GPIOService
from src.Server import Server



def check_light(light_sensor_connection: LightSensor, lcd_service, led_service, output):
    while True:
        print("light sensor")
        print("---------")

        light_level = light_sensor_connection.get_data()
        print("sensor: %5d" % (light_level))
        normized = (50000 - light_level) / 50000
        led_service.set_color(round(255 * normized), round(255 * (1 - normized)), 0)
        lcd_service.write_line('{:d}'.format(light_level))
        output({
            "light": light_level
        })


def check_bme680(bme680_sensor_connection: TemperatureSensor, output):
    while True:
        print("BME680 sensor")
        print("---------")

        data = bme680_sensor_connection.get_data()
        print("Temperature: ", data["temperature"])
        print("Gas: ", data["gas"])
        print("Humidity: ", data["humidity"])
        print("Pressure: ", data["pressure"])
        print("Altitude: ", data["altitude"])
        print("------------------")
        output(data)


def check_gyro(motion_sensor_connection: MotionSensor, output):
    while True:
        print("gyro data")
        print("---------")

        gyro = motion_sensor_connection.get_gyro()

        print("gyro_xout: ", gyro[0])
        print("gyro_yout: ", gyro[1])
        print("gyro_zout: ", gyro[2])

        print("")
        print("accelerometer data")
        print("------------------")

        accel = motion_sensor_connection.get_acceleration()

        accel_xout_scaled = accel[0] / 16384.0
        accel_yout_scaled = accel[1] / 16384.0
        accel_zout_scaled = accel[2] / 16384.0

        x_rotation = motion_sensor_connection.get_x_rotation(accel_xout_scaled, accel_yout_scaled, accel_zout_scaled)
        y_rotation = motion_sensor_connection.get_y_rotation(accel_xout_scaled, accel_yout_scaled, accel_zout_scaled)

        print("accel_xout: ", accel[0], " scaled: ", accel_xout_scaled)
        print("accel_yout: ", accel[1], " scaled: ", accel_yout_scaled)
        print("accel_zout: ", accel[2], " scaled: ", accel_zout_scaled)

        print("x rotation: ", x_rotation)
        print("y rotation: ", y_rotation)

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
        print("temp: ", temp)
        time.sleep(.500)






def main():
    bus = smbus2.SMBus(1)  # or bus = smbus.SMBus(1) for Revision 2 boards
    address = 0x68  # This is the address value read via the i2cdetect command
    lcd_service = LCDService()
    lcd_service.write_line("Hello")
    led_service = LEDService()
    bme_sensor = TemperatureSensor()
    motion_sensor = MotionSensor(I2CService(bus, address), 0)
    test = motion_sensor.start_up_gyro()
    print("gyro test result", test[0], test[1], test[2])

    gpio_service = GPIOService()
    light_sensor = LightSensor()
    buffer_filo = []


    server = Server(2048)
    server.start()

    def send_data(data):
        data_string = json.dumps(data)
        server.send_data(data_string)

    def save_bme_data(data):
        with open("bme680.txt", "a") as bme_file:
            data_line = f'{datetime.utcnow()},{data["temperature"]},{data["gas"]},{data["humidity"]},' \
                f'{data["pressure"]},{data["altitude"]}\n'
            print(data_line)
            bme_file.write(data_line)
    light_thread = threading.Thread(target=check_light, args=(light_sensor, lcd_service, led_service, send_data))
    gyro_thread = threading.Thread(target=check_gyro, args=(motion_sensor, send_data))
    bme_thread = threading.Thread(target=check_bme680, args=(bme_sensor, save_bme_data))
    light_thread.start()
    bme_thread.start()
    gyro_thread.start()
    light_thread.join()
    gyro_thread.join()
    server.join()


if __name__ == '__main__':
    main()
