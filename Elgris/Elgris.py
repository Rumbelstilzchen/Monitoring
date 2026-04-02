# -*- coding: utf-8 -*-

import json
import pickle
from datetime import datetime
import pytz
from retry import retry
import logging
import sunspec2.modbus.client as sp_client
from base_monitoring.monitorin_base_class import Base_Parser
import paho.mqtt.client as mqtt  # import the client1

logger = logging.getLogger(__name__)


def check_values_empty(dict_data):
    for value in dict_data.values():
        if value == "":
            return True
    return False


class Elgris(Base_Parser):
    name = "Elgris"

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
        self.accumulate_file = f"{self.name}_acucmulate.pkl"

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
        self.mqtt_client = None
        self.mqtt_topic = ""
        try:
            self.connect_mqtt()
        except Exception as e:
            logger.exception("Cannot connect to MQTT")
            raise e

    @retry(tries=4, delay=10, backoff=1.5, logger=logger)
    def connect_mqtt(self):
        if "MQTT_broker_ip" in self.configuration[self.name]:
            logger.info("Connecting to MQTT")
            self.mqtt_topic = self.configuration.get(self.name, "MQTT_topic")
            self.mqtt_client = mqtt.Client(
                mqtt.CallbackAPIVersion.VERSION2,
                client_id=f"{self.name}_logger",
                clean_session=False,
                protocol=4,
            )  # create new instance
            self.mqtt_client.will_set(
                f"equipment/{self.name}/connection", "offline", qos=1, retain=True
            )

            def on_connect(client, userdata, flags, reason_code, properties):
                logger.info(f"Connecting - setting online status - rc: {reason_code}")
                client.publish(
                    f"equipment/{Elgris.name}/connection",
                    "online",
                    qos=1,
                    retain=True,
                )

            self.mqtt_client.username_pw_set(
                self.configuration.get(self.name, "MQTT_user"),
                self.configuration.get(self.name, "MQTT_PW"),
            )
            self.mqtt_client.tls_set("ca.crt")
            self.mqtt_client.on_connect = on_connect
            self.mqtt_client.connect(
                host=self.configuration.get(self.name, "MQTT_broker_ip"),
                port=self.configuration.getint(self.name, "MQTT_broker_port"),
            )
            self.mqtt_client.loop_start()
            # self.mqtt_client.publish(f"equipment/{self.name}/status", 'online', qos=1, retain=True)

    def exit_parser(self):

        with open(self.accumulate_file, "wb") as f_handle:
            pickle.dump(
                self.accumulated_data, f_handle, protocol=pickle.HIGHEST_PROTOCOL
            )
            logger.info("Saved accumulated data")
        if self.mqtt_client is not None:
            try:
                self.mqtt_client.publish(
                    f"equipment/{self.name}/connection", "offline", qos=1, retain=True
                )
                logger.info('MQTT "offline"-status was set')
                self.mqtt_client.loop_stop()
            except Exception:
                logger.exception('MQTT failed to set "offline"-status')

    def collect_data(self):
        self.load_data_fromurl()
        self.add_extra_entries()
        self.accumulate_data()
        if self.mqtt_client is not None:
            self.mqtt_data.update(
                {
                    key: value
                    for key, value in self.parsed_data.items()
                    if key not in self.suppress_zeros
                }
            )
            self.mqtt_data.update(self.accumulated_data)
            self.send_mqtt_data()
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

    def send_mqtt_data(self):
        try:
            if not self.mqtt_client.is_connected():
                self.mqtt_client.reconnect()
            json_data = json.dumps(self.mqtt_data)
            self.mqtt_client.publish(self.mqtt_topic, json_data)
        except Exception:
            logger.exception("Error Sending date to mqtt_client - no retry")

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
