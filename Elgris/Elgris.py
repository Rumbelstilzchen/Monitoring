# -*- coding: utf-8 -*-

import json
from datetime import datetime
import pytz
from retry import retry
import logging
import sunspec2.modbus.client as client
from base_monitoring.monitorin_base_class import Base_Parser
import paho.mqtt.client as mqtt  # import the client1

logger = logging.getLogger(__name__)


def check_values_empty(dict_data):
    for value in dict_data.values():
        if value == "":
            return True
    return False


class Elgris(Base_Parser):
    name = 'Elgris'

    def __init__(self, config):
        super().__init__()
        self.configuration = config
        self.timestamp = None
        self.model = None
        self.ip_address = self.configuration[self.name]['IPAdresse']
        # self.time_zone = 'Europe/Berlin'
        self.time_zone = 'UTC'
        self.tz = pytz.timezone(self.time_zone)
        # 'PhVphA', 'PhVphB', 'PhVphC'
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
        self.mqtt_client = None
        self.mqtt_topic = ''
        if 'MQTT_broker_ip' in self.configuration[self.name]:
            try:
                self.mqtt_topic = self.configuration.get(self.name, 'MQTT_topic')
                self.mqtt_client = mqtt.Client(client_id=f"{self.name}_logger", clean_session=False,
                                               protocol=4)  # create new instance
                self.mqtt_client.will_set(f"equipment/{self.name}/connection", 'offline', qos=1, retain=True)

                def on_connect(client, userdata, flags, rc):
                    logger.info(f"Connecting - setting online status - rc: {rc}")
                    client.publish(f"equipment/{Elgris.name}/connection", 'online', qos=1, retain=True)

                self.mqtt_client.username_pw_set(self.configuration.get(self.name, 'MQTT_user'),
                                                 self.configuration.get(self.name, 'MQTT_PW'))
                self.mqtt_client.tls_set("ca.crt")
                self.mqtt_client.on_connect = on_connect
                self.mqtt_client.connect(host=self.configuration.get(self.name, 'MQTT_broker_ip'),
                                         port=self.configuration.getint(self.name, 'MQTT_broker_port'))
                self.mqtt_client.loop_start()
                # self.mqtt_client.publish(f"equipment/{self.name}/status", 'online', qos=1, retain=True)

            except Exception:
                logger.exception('Cannot connect to mqtt broker ignoring for this run')
                self.mqtt_client = None

    def exit_parser(self):
        if self.mqtt_client is not None:
            try:
                self.mqtt_client.publish(f"equipment/{self.name}/status", 'offline', qos=1, retain=True)
                logger.info('MQTT "offline"-status was set')
                self.mqtt_client.loop_stop()
            except Exception:
                logger.exception('MQTT failed to set "offline"-status')

    def collect_data(self):
        self.load_data_fromurl()
        self.add_extra_entries()
        if self.mqtt_client is not None:
            self.send_mqtt_data()
        return self.parsed_data

    def send_mqtt_data(self):
        try:
            if not self.mqtt_client.is_connected():
                self.mqtt_client.reconnect()
            json_data = json.dumps(self.parsed_data)
            self.mqtt_client.publish(self.mqtt_topic, json_data)
        except Exception:
            logger.exception('Error Sending date to mqtt_client - no retry')

    @staticmethod
    def reformat_data(input_dict, dictionary):
        output = {}
        for x in input_dict:
            output[dictionary[x['dxsId']]] = x['value']
        return output

    @retry(tries=2, delay=0)
    def load_data_fromurl(self):
        self.timestamp = datetime.now(self.tz)
        self.model.models['ac_meter'][0].read()
        for key, value in self.IDs.items():
            if value[1] is not None:
                self.parsed_data[value[0]] = round(self.model.models['ac_meter'][0].points[key].value * value[1],
                                                   value[2])
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
