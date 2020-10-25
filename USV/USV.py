# -*- coding: utf-8 -*-

import logging
# import telnetlib
# import urllib.request
import pytz
from datetime import datetime
from nut2 import PyNUTClient
# from retry import retry
from collections import OrderedDict

logger = logging.getLogger(__name__)


class USV:
    name = 'USV'

    def __init__(self, config=None):
        self.configuration = config
        self.timestamp = None
        self.http = None
        self.parsed_data = OrderedDict()
        # self.time_zone = 'Europe/Berlin'
        self.time_zone = 'UTC'
        self.tz = pytz.timezone(self.time_zone)
        self.nut_name = "ups"

        self.nut = PyNUTClient(host=self.configuration[self.name]['IPAdresse'], debug=False, connect=False)
        self.parsed_data = None
        self.id_fields = {
            "battery.charge": ["battery_charge", int],
            # "battery.charge.low": "10",
            # "battery.charge.warning": "50",
            # "battery.date": "2001/09/25",
            # "battery.mfr.date": "2019/04/27",
            "battery.runtime": ["battery_runtime", int],
            # "battery.runtime.low": "battery_runtime_low",
            # "battery.type": "PbAc
            "battery.voltage": ["battery_voltage", float],
            # "battery.voltage.nominal": "12.0
            # "device.mfr": "American Power Conversion
            # "device.model": "Back-UPS XS 700U
            # "device.serial": "3B1917X69838
            # "device.type": "ups
            # "driver.name": "usbhid-ups
            # "driver.parameter.pollfreq": "30
            # "driver.parameter.pollinterval": "5
            # "driver.parameter.port": "auto
            # "driver.version": "DSM6-2-25364-191230
            # "driver.version.data": "APC HID 0.95
            # "driver.version.internal": "0.38
            # "input.sensitivity": "high
            # "input.transfer.high": "290
            # "input.transfer.low": "140
            "input.voltage": ["input_voltage", float],
            # "input.voltage.nominal": "230
            # "ups.beeper.status": "enabled
            # "ups.delay.shutdown": "20
            # "ups.firmware": "924.Z3 .I
            # "ups.firmware.aux": "Z3
            "ups.load": ["ups_load", int],
            # "ups.mfr": "American Power Conversion
            # "ups.mfr.date": "2019/04/27
            # "ups.model": "Back-UPS XS 700U
            # "ups.productid": "0002
            "ups.realpower.nominal": ["nominal_power", int],
            # "ups.serial": "3B1917X69838
            "ups.status": ["ups_status", str],
            # "ups.test.result": "No test initiated
            # "ups.timer.reboot": "0
            # "ups.timer.shutdown": "-1
            # "ups.vendorid": "051d
        }
        self.average_ignores = [
            'TIMESTAMP',
            'time_sec',
            'ups_status',
        ]

    def collect_data(self):
        self.load_data()
        self.add_extra_entries()
        return self.parsed_data

    # @staticmethod
    # def reformat_data(input_dict, dictionary):
    #     output = OrderedDict()
    #     for x in input_dict:
    #         output[dictionary[x['dxsId']]] = x['value']
    #     return output

    # @retry(tries=2, delay=0)
    def load_data(self):
        data = OrderedDict()
        self.nut._connect()
        self.timestamp = datetime.now(self.tz)
        for key in self.id_fields.keys():
            data[self.id_fields[key][0]] = self.id_fields[key][1](self.nut.get_var(self.nut_name, key))
            # print(self.nut.var_description(self.nut_name,key))
            # try:
            #     print(str(self.nut.list_range(self.nut_name,key)))
            # except:
            #     pass
        self.parsed_data = data

    def add_extra_entries(self):
        self.parsed_data['time_sec'] = int(self.timestamp.timestamp())
        self.parsed_data['TIMESTAMP'] = datetime.fromtimestamp(
            self.parsed_data['time_sec'], self.tz).strftime('%Y-%m-%d %H:%M:%S')

    def correct_data(self):
        pass


if __name__ == "__main__":
    logger.error('logger file needs to be run directly')
