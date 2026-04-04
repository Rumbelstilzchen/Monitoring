# -*- coding: utf-8 -*-

import logging
import pytz
from datetime import datetime

from future.utils import reraise
from nut2 import PyNUTClient
from base_classes.monitorin_base_class import Base_Parser
from retry import retry

logger = logging.getLogger(__name__)


class USV(Base_Parser):
    name = 'USV'

    id_fields = {
        "battery.charge": ["battery_charge", float],
        # "battery.charge.low": "10",
        # "battery.charge.warning": "50",
        # "battery.date": "2001/09/25",
        # "battery.mfr.date": "2019/04/27",
        "battery.runtime": ["battery_runtime", float],
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
        "ups.load": ["ups_load", float],
        # "ups.mfr": "American Power Conversion
        # "ups.mfr.date": "2019/04/27
        # "ups.model": "Back-UPS XS 700U
        # "ups.productid": "0002
        # "ups.realpower.nominal": ["nominal_power", int],
        # "ups.serial": "3B1917X69838
        "ups.status": ["ups_status", str],
        # "ups.test.result": "No test initiated
        # "ups.timer.reboot": "0
        # "ups.timer.shutdown": "-1
        # "ups.vendorid": "051d
    }


    def __init__(self, config=None):
        super().__init__()
        self.configuration = config
        try:
            self.refreshrate = self.configuration.getint(self.name, "refreshrate")
        except Exception:
            self.refreshrate = 2
        self.timeout = max(min(10, self.refreshrate - 2), 2)
        self.ip_address = self.configuration[self.name]["IPAdresse"]
        # self.time_zone = 'Europe/Berlin'
        self.time_zone = "UTC"
        self.tz = pytz.timezone(self.time_zone)
        self.timestamp = datetime.now(self.tz)

        self.nut_name = "ups"

        self.nut = PyNUTClient(host=self.ip_address, debug=False, connect=False, timeout=self.timeout)
        self.parsed_data = None
        self.nominal_power_factor = self.configuration[self.name].get("nominal_power", 500) / 100.0
        self.average_ignores = [
            'TIMESTAMP',
            'time_sec',
            'ups_status',
        ]
        self.nut._connect()
        try:
            connected_usvs = self.nut.list_ups()
        except Exception as e:
            logger.exception('Error connecting to NUT')
            raise e
        if self.nut_name not in connected_usvs:
            logger.warning('UPS with name %s not found. Connected UPS: %s', self.nut_name, connected_usvs)
            if connected_usvs:
                self.nut_name = connected_usvs[0]
                logger.warning('Using UPS with name %s instead', self.nut_name)
            else:
                raise RuntimeError('No UPS connected')

    def collect_data(self):
        self.load_data()
        self.add_extra_entries()
        return self.parsed_data

    # @staticmethod
    # def reformat_data(input_dict, dictionary):
    #     output = {}
    #     for x in input_dict:
    #         output[dictionary[x['dxsId']]] = x['value']
    #     return output

    @retry(tries=2, delay=0)
    def load_data(self):
        data = {}
        self.nut._connect()
        self.timestamp = datetime.now(self.tz)
        for key, item in self.id_fields.items():
            try:
                data[item[0]] = item[1](self.nut.get_var(self.nut_name, key))
            except Exception:
                logger.exception('Error loading data for key %s', key)
                data[item[0]] = None
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
        self.parsed_data['nominal_power'] = self.parsed_data['ups_load'] * self.nominal_power_factor
        #self.parsed_data['nominal_power'] = 500

    def correct_data(self):
        pass


if __name__ == "__main__":
    logger.error('logger file needs to be run directly')
