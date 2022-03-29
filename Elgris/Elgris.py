# -*- coding: utf-8 -*-

import json
from datetime import datetime
import pytz
from retry import retry
from collections import OrderedDict
import logging
import urllib3
import sunspec2.modbus.client as client

logger = logging.getLogger(__name__)


def check_values_empty(dict_data):
    for value in dict_data.values():
        if value == "":
            return True
    return False


class Elgris:
    name = 'Elgris'

    def __init__(self, config):
        self.configuration = config
        self.timestamp = None
        self.model = None
        self.ip_address = self.configuration[self.name]['IPAdresse']
        self.parsed_data = OrderedDict()
        # self.time_zone = 'Europe/Berlin'
        self.time_zone = 'UTC'
        self.tz = pytz.timezone(self.time_zone)
        'PhVphA', 'PhVphB', 'PhVphC'
        self.IDs = {  # id of readback: ['name in DB', Scaling factor, number of digits]
            'PhVphA': ['GridVoltageL1', 0.01, 1],
            'PhVphB': ['GridVoltageL2', 0.01, 1],
            'PhVphC': ['GridVoltageL3', 0.01, 1],
            'W': ['Power_W', None],
            # 'TotWhImp': ['total_Wh', None],
        }
        self.average_ignores = [
            'TIMESTAMP',
            'time_sec',
            'TotWhImp'
        ]
        self.model = client.SunSpecModbusClientDeviceTCP(ipaddr=self.ip_address)
        self.model.scan()

    def collect_data(self):
        self.load_data_fromurl()
        self.add_extra_entries()
        return self.parsed_data



    @retry(tries=2, delay=0)
    def load_data_fromurl(self):

        self.timestamp = datetime.now(self.tz)
        self.model.models['ac_meter'][0].read()
        for key, value in self.IDs.items():
            if value[1] is not None:
                self.parsed_data[value[0]] = round(self.model.models['ac_meter'][0].points[key].value * value[1], value[2])
            else:
                self.parsed_data[value[0]] = self.model.models['ac_meter'][0].points[key].value*1.0


    def add_extra_entries(self):
        self.parsed_data['time_sec'] = int(self.timestamp.timestamp())
        self.parsed_data['TIMESTAMP'] = datetime.fromtimestamp(
            self.parsed_data['time_sec'], self.tz).strftime('%Y-%m-%d %H:%M:%S')



def manual_read_and_print_data():
    parser = Elgris
    import configparser
    configuration = configparser.ConfigParser()
    configuration.sections()
    configuration.read(r'..\config.ini')

    parser_init = parser(configuration)

    for key, value in parser_init.collect_data().items():
        print(f'{key}:\t{value} - type {type(value)}')


if __name__ == "__main__":
    logger.warning('For monitoring, script needs to be run by: python monitoring_template.py Luxtronik')
    manual_read_and_print_data()
