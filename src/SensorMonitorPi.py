#!/usr/bin/python

import smbus2
import time
import threading
import json

from src.I2CService import I2CService
from src.MotionSensor import MotionSensor
from src.LightSensor import LightSensor
from src.GPIOService import GPIOService
from src.Server import Server

bus = smbus2.SMBus(1)  # or bus = smbus.SMBus(1) for Revision 2 boards
address = 0x68  # This is the address value read via the i2cdetect command

motion_sensor = MotionSensor(I2CService(bus, address), 0)
test = motion_sensor.start_up_gyro()
print("gyro test result", test[0], test[1], test[2])

gpio_service = GPIOService()
light_sensor = LightSensor()
buffer_filo = []


def check_light(light_sensor_connection: LightSensor, output):
    while True:
        print("light sensor")
        print("---------")
        light_level = light_sensor_connection.get_data()
        print("sensor: %5d" % (light_level))
        output({
            "light": light_level
        })


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


server = Server(2048)
server.start()


def send_data(data):
    data_string = json.dumps(data)
    server.send_data(data_string)


light_thread = threading.Thread(target=check_light, args=(light_sensor, send_data))
gyro_thread = threading.Thread(target=check_gyro, args=(motion_sensor, send_data))
light_thread.start()
gyro_thread.start()
light_thread.join()
gyro_thread.join()
server.join()
