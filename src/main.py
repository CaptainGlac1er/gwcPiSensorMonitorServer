import getopt
import sys
import threading
import time

from datetime import datetime, date

from TemperatureSensor import TemperatureSensor


def check_bme680(bme680_sensor_connection: TemperatureSensor, output):
    while True:
        data = bme680_sensor_connection.get_data()
        output(data)
        time.sleep(1)


def main(argv):
    bme_sensor = TemperatureSensor()
    optlist, args = getopt.getopt(argv, '', ['output-folder='])
    folder = None
    for option, argument in optlist:
        if option == "--output-folder":
            folder = argument
    if folder is None:
        exit(1)
    bme680_file = f'{folder}/bme680-{date.today()}.csv'
    def save_bme_data(data):
        with open(bme680_file, "a") as bme_file:
            data_line = f'{datetime.utcnow()}, {data["temperature"]}, {data["gas"]}, {data["humidity"]}, ' \
                f'{data["pressure"]}, {data["altitude"]}\n'
            print(data_line)
            bme_file.write(data_line)

    bme_thread = threading.Thread(target=check_bme680, args=(bme_sensor, save_bme_data))
    bme_thread.start()


if __name__ == '__main__':
    main(sys.argv[1:])
