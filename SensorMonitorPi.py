#!/usr/bin/python

import smbus2
import time

from I2CService import I2CService
from MotionSensor import MotionSensor

bus = smbus2.SMBus(1) # or bus = smbus.SMBus(1) for Revision 2 boards
address = 0x68       # This is the address value read via the i2cdetect command

motion_sensor = MotionSensor(I2CService(bus, address), 0)
test = motion_sensor.start_up_gyro()
print("gyro test result", test[0], test[1], test[2])

while True:
    print("gyro data")
    print("---------")

    gyro = motion_sensor.get_gyro()

    print("gyro_xout: ", gyro[0])
    print("gyro_yout: ", gyro[1])
    print("gyro_zout: ", gyro[2])

    print("")
    print("accelerometer data")
    print("------------------")

    accel = motion_sensor.get_acceleration()

    accel_xout_scaled = accel[0] / 16384.0
    accel_yout_scaled = accel[1] / 16384.0
    accel_zout_scaled = accel[2] / 16384.0

    print("accel_xout: ", accel[0], " scaled: ", accel_xout_scaled)
    print("accel_yout: ", accel[1], " scaled: ", accel_yout_scaled)
    print("accel_zout: ", accel[2], " scaled: ", accel_zout_scaled)

    print("x rotation: ", motion_sensor.get_x_rotation(accel_xout_scaled, accel_yout_scaled, accel_zout_scaled))
    print("y rotation: ", motion_sensor.get_y_rotation(accel_xout_scaled, accel_yout_scaled, accel_zout_scaled))

    temp = motion_sensor.get_temp()
    print("temp: ", temp)
    time.sleep(.500)