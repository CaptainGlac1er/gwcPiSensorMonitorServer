import math
from src import I2CService


class MotionSensor:
    GYRO_CONFIG_REG = 0x1B
    GYRO_LSB = [
        131,
        65.5,
        32.8,
        16.4
    ]
    INT_ENABLE_REG = 0x38
    INT_STATUS_REG = 0x3A

    Gyro_mode = 0
    I2C_service = None  # type: I2CService

    # Power management registers
    power_mgmt_1 = 0x6b
    power_mgmt_2 = 0x6c

    Gyro_calibration_data = {}

    def __init__(self, i2c_service: I2C_service, gyro_mode):
        if gyro_mode > 3 or gyro_mode < 0:
            raise Exception('Must be be contained within 0 and 3')
        self.I2C_service = i2c_service
        self.I2C_service.write_byte(self.power_mgmt_1, 0)
        self.Gyro_mode = gyro_mode
        self.setup_sensor()
        self.calibrate(20)

    def setup_sensor(self):
        before = self.I2C_service.read_byte(MotionSensor.INT_ENABLE_REG)
        before |= 0b1
        self.I2C_service.write_byte(MotionSensor.INT_ENABLE_REG, before)

    def wait_for_data(self):
        while(True):
            if self.I2C_service.read_byte(MotionSensor.INT_STATUS_REG) & 1 == 1:
                return True

    def calibrate(self, n_samples):
        samples = {}
        for i in range(n_samples):
            data = self.get_gyro()
            for key in range(len(data)):
                samples[key] = samples.get(key, 0) + (data[key] / n_samples)
        self.Gyro_calibration_data = samples

    @staticmethod
    def dist(a, b):
        return math.sqrt((a * a) + (b * b))

    def get_y_rotation(self, x, y, z):
        radians = math.atan2(x, self.dist(y, z))
        return -math.degrees(radians)

    def get_x_rotation(self, x, y, z):
        radians = math.atan2(y, self.dist(x, z))
        return math.degrees(radians)

    def start_up_gyro(self):
        self.wait_for_data()
        before = self.get_gyro()
        init = self.I2C_service.read_byte(MotionSensor.GYRO_CONFIG_REG)
        # self test X
        init |= 0b10000000
        # self test Y
        init |= 0b01000000
        # self test Z
        init |= 0b00100000
        # set mode
        init &= (0b11100111 | self.Gyro_mode << 3)
        self.I2C_service.write_byte(MotionSensor.GYRO_CONFIG_REG, init)
        self.wait_for_data()
        after = self.get_gyro()
        return [x - y for x, y in zip(after, before)]

    def get_gyro(self) -> list:
        self.wait_for_data()
        return [
            self.I2C_service.read_word_2c(0x43) / self.GYRO_LSB[self.Gyro_mode] - self.Gyro_calibration_data.get(0, 0),
            self.I2C_service.read_word_2c(0x45) / self.GYRO_LSB[self.Gyro_mode] - self.Gyro_calibration_data.get(1, 0),
            self.I2C_service.read_word_2c(0x47) / self.GYRO_LSB[self.Gyro_mode] - self.Gyro_calibration_data.get(2, 0)
        ]

    def get_acceleration(self):
        self.wait_for_data()
        return [
            self.I2C_service.read_word_2c(0x3b),
            self.I2C_service.read_word_2c(0x3d),
            self.I2C_service.read_word_2c(0x3f)
        ]

    def get_temp(self):
        self.wait_for_data()
        return int(self.I2C_service.read_word_2c(0x41)) / 340.0 + 36.53
