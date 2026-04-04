# -*- coding: utf-8 -*-

import base64
import hashlib
import json
import logging
import pickle
from datetime import datetime
from itertools import islice

import pytz
import urllib3
from retry import retry

from base_classes.monitorin_base_class import Base_Parser
from base_classes.mqtt import MQTTBase

logger = logging.getLogger(__name__)


def chunks(data, SIZE=25):
    it = iter(data)
    for i in range(0, len(data), SIZE):
        yield {k: data[k] for k in islice(it, SIZE)}


def check_values_empty(dict_data):
    for value in dict_data.values():
        if value == "":
            return True
    return False



class GoE_Garage(Base_Parser):
    name = "GoE_Garage"
    nrg_mapping = {
        0: 'GridVoltageL1',
        # 1: 'GridVoltageL2',
        # 2: 'GridVoltageL3',
        # 3: 'GridVoltageN',
        # 4: 'BatPowerLadenL1',
        # 5: 'BatPowerLadenL2',
        # 6: 'BatPowerLadenL3',
        7: 'BatPowerLaden',
    }
    influx_tags = {
        "BatPowerLaden": (
            "power",
            float,
            {
                "measurement": "car_battery",
                "tags": {
                    "flow_type": "ac",
                    "flow_source": "home",
                    "flow_destination": "car",
                    "type": "power",
                    "unit": "W",
                    "device": "GoE_Garage",
                },
            },
        ),

        # "BatStateOfCharge": (
        #     "SOC",
        #     int,
        #     {
        #         "measurement": "byd_battery",
        #         "tags": {"type": "SOC", "unit": "'%'", "device": "GoE_Garage"},
        #     },
        # ),

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
                    "device": "GoE_Garage",
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
                    "device": "GoE_Garage",
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
                    "device": "GoE_Garage",
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
        self.http = None
        self.mqtt_data = {}
        # self.time_zone = 'Europe/Berlin'
        self.time_zone = "UTC"
        self.tz = pytz.timezone(self.time_zone)
        self.timestamp = datetime.now(self.tz)

        self.average_ignores = [
            "TIMESTAMP",
            "time_sec",
        ]

        self.last_day = self.timestamp.astimezone(
            tz=pytz.timezone("Europe/Berlin")
        ).date()
        self.accumulate_file = f"{self.name}_acucmulate.pkl"

        try:
            with open(self.accumulate_file, "rb") as f_handle:
                self.accumulated_data = pickle.load(f_handle)
            logger.info("Loaded accumulated data")
        except Exception:
            self.accumulated_data = {
                "bat_imported": 0,
                # '': 0,
                # '': 0,
                # '': 0,
            }
        self.mqtt = None
        mqtt_base_topic = self.configuration[self.name]["mqtt_base_topic"]
        self.mqtt_topics = [f'{mqtt_base_topic}/nrg']
        try:
            self.mqtt = MQTTBase(self.name, self.configuration[self.name].get('mqtt', None), self.suppress_zeros, topics=self.mqtt_topics, receiver_method=self._on_message)
        except Exception as e:
            logger.exception("Cannot connect to MQTT")
            raise e
        self.mqtt_data = {}



    def _on_message(self, client, userdata, msg):
        try:
            current_data = json.loads(msg.payload.decode("utf-8"))

            self.mqtt_data = {name: current_data[key] for key, name in self.nrg_mapping.items() }
            # print(self.mqtt_data)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON received: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in message handler: {e}")

    def exit_parser(self):

        with open(self.accumulate_file, "wb") as f_handle:
            pickle.dump(
                self.accumulated_data, f_handle, protocol=pickle.HIGHEST_PROTOCOL
            )
            logger.info("Saved accumulated data")

    def collect_data(self):
        self.parsed_data = self.load_data_fromurl()
        self.add_extra_entries()

        return self.parsed_data


    @staticmethod
    def reformat_data(input_dict, dictionary):
        # output = {}
        # for x in input_dict:
        #    output[dictionary[x['dxsId']]] = x['value']
        output = {dictionary[x["dxsId"]]: x["value"] for x in input_dict}
        return output

    @retry(tries=2, delay=0)
    def load_data_fromurl(self):
        self.timestamp = datetime.now(self.tz)
        return self.mqtt_data

    def add_extra_entries(self):
        self.parsed_data["time_sec"] = int(self.timestamp.timestamp())
        self.parsed_data["TIMESTAMP"] = datetime.fromtimestamp(
            self.parsed_data["time_sec"], self.tz
        ).strftime("%Y-%m-%d %H:%M:%S")



if __name__ == "__main__":
    logger.error("logger file needs to be run directly")
