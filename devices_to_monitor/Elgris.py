# -*- coding: utf-8 -*-

import os
import pickle
from datetime import datetime
import pytz
from retry import retry
import logging
import sunspec2.modbus.client as sp_client
from base_classes.monitorin_base_class import Base_Parser
from base_classes.mqtt import MQTTBase

logger = logging.getLogger(__name__)


def check_values_empty(dict_data):
    for value in dict_data.values():
        if value == "":
            return True
    return False


class Elgris(Base_Parser):
    name = "Elgris"
    influx_tags = {
        "Power_W": (
            "power",
            float,
            {
                "measurement": "wp",
                "tags": {
                    "flow_type": "ac",
                    "flow_source": "home",
                    "flow_destination": "wp",
                    "type": "power",
                    "unit": "W",
                    "device": "elgris",
                },
            },
        ),
        "GridVoltageL1": (
            "voltage",
            float,
            {
                "measurement": "grid",
                "tags": {
                    "origin": "L1",
                    "flow_type": "ac",
                    "type": "voltage",
                    "unit": "V",
                    "device": "elgris",
                },
            },
        ),
        "GridVoltageL2": (
            "voltage",
            float,
            {
                "measurement": "grid",
                "tags": {
                    "origin": "L2",
                    "flow_type": "ac",
                    "type": "voltage",
                    "unit": "V",
                    "device": "elgris",
                },
            },
        ),
        "GridVoltageL3": (
            "voltage",
            float,
            {
                "measurement": "grid",
                "tags": {
                    "origin": "L3",
                    "flow_type": "ac",
                    "type": "voltage",
                    "unit": "V",
                    "device": "elgris",
                },
            },
        ),
    }

    def __init__(self, config):
        super().__init__()
        self.configuration = config
        try:
            self.refreshrate = self.configuration.getint(self.name, "refreshrate")
        except Exception:
            self.refreshrate = 2
        self.timeout = max(min(10, self.refreshrate - 2), 2)
        self.model = None
        self.mqtt_data = {}
        self.ip_address = self.configuration[self.name]["IPAdresse"]
        # self.time_zone = 'Europe/Berlin'
        self.time_zone = "UTC"
        self.tz = pytz.timezone(self.time_zone)
        self.timestamp = datetime.now(self.tz)
        # 'PhVphA', 'PhVphB', 'PhVphC'
        self.IDs = {  # id of readback: ['name in DB', Scaling factor, number of digits]
            "PhVphA": ["GridVoltageL1", 0.01, 1],
            "PhVphB": ["GridVoltageL2", 0.01, 1],
            "PhVphC": ["GridVoltageL3", 0.01, 1],
            "W": ["Power_W", None],
            # 'TotWhImp': ['total_Wh', None],
        }
        self.average_ignores = ["TIMESTAMP", "time_sec", "TotWhImp"]
        self.model = sp_client.SunSpecModbusClientDeviceTCP(
            ipaddr=self.ip_address, timeout=self.timeout
        )
        self.model.scan()
        model_strs = [
            keys
            for keys in self.model.models
            if isinstance(keys, str) and keys.startswith("ac_meter")
        ]
        self.model_str = model_strs[0]
        self.last_day = self.timestamp.astimezone(
            tz=pytz.timezone("Europe/Berlin")
        ).date()
        logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")

        self.accumulate_file = os.path.join(logs_dir, f"{self.name}_acucmulate.pkl")

        try:
            with open(self.accumulate_file, "rb") as f_handle:
                self.accumulated_data = pickle.load(f_handle)
            logger.info("Loaded accumulated data")
        except Exception:
            self.accumulated_data = {
                "total_energy": 0,
                # '': 0,
                # '': 0,
                # '': 0,
            }
        self.mqtt = None
        try:
            self.mqtt = MQTTBase(self.name, self.configuration[self.name].get('mqtt', None), self.suppress_zeros)
            # self.set_averages = self.mqtt.handle_mqtt_averages
        except Exception as e:
            logger.exception("Cannot connect to MQTT")
            raise e


    def exit_parser(self):

        with open(self.accumulate_file, "wb") as f_handle:
            pickle.dump(
                self.accumulated_data, f_handle, protocol=pickle.HIGHEST_PROTOCOL
            )
            logger.info("Saved accumulated data")

    def collect_data(self):
        self.load_data_fromurl()
        self.add_extra_entries()
        self.accumulate_data()
        self.mqtt.send_data(self.parsed_data, **self.accumulated_data)
        return self.parsed_data

    def accumulate_data(self):
        today = self.timestamp.astimezone(tz=pytz.timezone("Europe/Berlin")).date()
        if today > self.last_day:
            self.last_day = today
            logger.info("New day reset accumulated data")
            self.accumulated_data = {key: 0 for key in self.accumulated_data}
        self.accumulated_data["total_energy"] += (
            self.parsed_data["Power_W"] * self.refreshrate / 3600
        )


    @retry(tries=2, delay=0)
    def load_data_fromurl(self):
        self.timestamp = datetime.now(self.tz)
        self.model.models[self.model_str][0].read()
        for key, value in self.IDs.items():
            if value[1] is not None:
                self.parsed_data[value[0]] = round(
                    self.model.models[self.model_str][0].points[key].value * value[1],
                    value[2],
                )
            else:
                self.parsed_data[value[0]] = (
                    self.model.models[self.model_str][0].points[key].value * 1.0
                )

    def add_extra_entries(self):
        self.parsed_data["time_sec"] = int(self.timestamp.timestamp())
        self.parsed_data["TIMESTAMP"] = datetime.fromtimestamp(
            self.parsed_data["time_sec"], self.tz
        ).strftime("%Y-%m-%d %H:%M:%S")


def manual_read_and_print_data():
    parser = Elgris
    import configparser

    configuration = configparser.ConfigParser()
    configuration.sections()
    configuration.read(r"..\config.ini")

    parser_init = parser(configuration)

    for key, value in parser_init.collect_data().items():
        print(f"{key}:\t{value} - type {type(value)}")


if __name__ == "__main__":
    logger.warning(
        "For monitoring, script needs to be run by: python monitoring_template.py Luxtronik"
    )
    manual_read_and_print_data()
