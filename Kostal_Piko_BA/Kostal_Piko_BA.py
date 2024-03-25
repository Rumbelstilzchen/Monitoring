# -*- coding: utf-8 -*-

import json
from datetime import datetime
import pytz
from retry import retry
import logging
import urllib3
from base_monitoring.monitorin_base_class import Base_Parser
import paho.mqtt.client as mqtt  # import the client1

logger = logging.getLogger(__name__)


def check_values_empty(dict_data):
    for value in dict_data.values():
        if value == "":
            return True
    return False


class Kostal_Piko_BA(Base_Parser):
    name = 'Kostal_Piko_BA'

    def __init__(self, config):
        super().__init__()
        self.configuration = config
        self.timestamp = None
        self.http = None
        # self.time_zone = 'Europe/Berlin'
        self.time_zone = 'UTC'
        self.tz = pytz.timezone(self.time_zone)
        self.dict_dxsID = [
            # {167772417: 'Analog1',
            # 167772673: 'Analog2',
            # 167772929: 'Analog3',
            # 167773185: 'Analog4',
            # 33556249: 'dischargeHysteresisOn'  # minimal Watt for usage of battery
            # 83888896: 'wintermode',
            # 83888640: 'eps',
            # 33556484: 'weatherForecast'
            # 33556239: 'chargeTimeStart',
            # 33556240: 'chargeTimeEnd',
            # 33556236: 'maintenanceCharge',
            # 33556231: 'minSoCManual',
            # 33556232: 'minSoCManualInc',
            # 33556233: 'minSoCManualIncStart',
            # 33556234: 'minSoCManualIncEnd',
            # 33556247: 'minSoCAutomatic',
            # 33556248: 'minSoCDynamic',

            # 33556482: 'pvModuleRegulation',
            # 67110913: 'overvoltageProtectionAc',
            # 117441537: 'portalCode',
            # 117441539: 'portalExport',
            # 201326848: 'S0Function',
            # 201327105: 'OwnConsumpCtrlFunction',
            # 201327113: 'DelayError',
            # 201327106: 'DelayErrorEnable',
            # 201327107: 'Fc1PowerThreshold',
            # 201327108: 'Fc1ExceedTime',
            # 201327109: 'Fc1Runtime',
            # 201327110: 'Fc1MaxActivationsDay',
            # 201327111: 'Fc2ThresholdOn',
            # 201327112: 'Fc2ThresholdOff',
            # 201327114: 'UseBattery'
            # },
            {33556226: 'BatVoltage',
             33556238: 'BatCurrent',
             33556230: 'BatCurrentDir',
             33556228: 'ChargeCycles',
             33556227: 'BatTemperature',
             33556229: 'BatStateOfCharge',
             83886336: 'AktHomeConsumptionSolar',
             83886592: 'AktHomeConsumptionBat',
             83886848: 'AktHomeConsumptionGrid',
             # 83888128: 'AktHomeConsumptionSolarBat',
             # 251658753: 'ErtragGesamt',
             # 251658496: 'Betriebszeit',
             # 251659009: 'HausverbrauchGesamt',
             # 251659265: 'EigenverbrauchGesamt',
             # 251659280: 'EigenverbrauchsquoteGesamt',
             # 251659281: 'AutarkiegradGesamt',
             # 251658754: 'ErtragHeute',
             # 251659010: 'HausverbrauchHeute',
             # 251659266: 'EigenverbrauchHeute',
             # 251659278: 'EigenverbrauchsquoteHeute',
             # 251659279: 'AutarkiegradHeute',
             # 117441538: 'CurrentPortal',
             # 117441542: 'TimeSinceLatestConnectionToPortal',
             83887872: 'AktHomeConsumption',
             33555203: 'dc1Power',
             33555459: 'dc2Power',
             # 33555715: 'dc3Power',
             33556736: 'dcPowerPV',
             67109120: 'acPower',
             16780032: 'operatingStatus'},
            {67110400: 'GridFreq',
             67110656: 'GridCosPhi',
             67110144: 'GridLimitation',
             # 67109379: 'GridPowerL1',
             # 67109635: 'GridPowerL2',
             # 67109891: 'GridPowerL3',
             67109378: 'GridVoltageL1',
             67109634: 'GridVoltageL2',
             67109890: 'GridVoltageL3',
             # 67109377: 'GridCurrentL1',
             # 67109633: 'GridCurrentL2',
             # 67109889: 'GridCurrentL3',
             # 83887106: 'AktHomeConsumptionL1',
             # 83887362: 'AktHomeConsumptionL2',
             # 83887618: 'AktHomeConsumptionL3',
             33555202: 'dc1Voltage',
             33555201: 'dc1Current',
             33555458: 'dc2Voltage',
             33555457: 'dc2Current',
             # 33555714: 'dc3Voltage',
             # 33555713: 'dc3Current',
             # 83888128: 'ownConsumption',
             16780032: 'operatingStatus'}
        ]
        self.nr_of_decimal_for_round['BatCurrentDir'] = 0
        self.average_ignores = [
            'TIMESTAMP',
            'time_sec',
            'operatingStatus',
            'ChargeCycles',
            'MaxVolPos',
            'MinVolPos',
            'MaxTempPos',
            'MinTempPos',
            'CycleCounts'
        ]
        self.suppress_zeros = [
            'BatVoltage',
            'BatCurrent',
            'BatTemperature',
            'BatStateOfCharge',
        ]
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
                    client.publish(f"equipment/{Kostal_Piko_BA.name}/connection", 'online', qos=1, retain=True)

                self.mqtt_client.username_pw_set(self.configuration.get(self.name, 'MQTT_user'),
                                                 self.configuration.get(self.name, 'MQTT_PW'))
                self.mqtt_client.tls_set("ca.crt")
                # self.mqtt_client.tls_insecure_set(False)
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
        self.correct_data()
        self.add_batLadenFrei()
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
        data = {}
        base_url = "http://" + self.configuration[self.name]['IPAdresse'] + "/api/dxs.json?"
        self.timestamp = datetime.now(self.tz)
        if self.http is None:
            self.http = urllib3.PoolManager()
        for dxs_set in self.dict_dxsID:
            dxs_string = '&dxsEntries='.join(str(v) for v in dxs_set.keys())

            json_url = self.http.request('GET', base_url + 'dxsEntries=' + dxs_string, retries=False)
            url_response = json.loads(json_url.data.decode('utf-8'))
            data.update(self.reformat_data(url_response['dxsEntries'], dxs_set))
            # with urllib.request.urlopen(base_url + 'dxsEntries=' + dxs_string, timeout=1) as json_url:
            #     url_response = json.loads(json_url.read().decode('utf8'))
            #     data.update(self.reformat_data(url_response['dxsEntries'], dxs_set))
            if check_values_empty(data):
                logger.error('empty strings were found')
                raise ValueError('empty strings were found')
        self.parsed_data = data

    def add_extra_entries(self):
        self.parsed_data['time_sec'] = int(self.timestamp.timestamp())
        self.parsed_data['TIMESTAMP'] = datetime.fromtimestamp(
            self.parsed_data['time_sec'], self.tz).strftime('%Y-%m-%d %H:%M:%S')
        if self.parsed_data['BatCurrentDir'] == 0:
            self.parsed_data['BatPowerLaden'] = self.parsed_data['BatCurrent'] * self.parsed_data['BatVoltage']
        else:
            self.parsed_data['BatPowerLaden'] = 0

        if self.parsed_data['BatCurrentDir'] == 1:
            self.parsed_data['BatPowerEntLaden'] = self.parsed_data['BatCurrent'] * self.parsed_data['BatVoltage']
        else:
            self.parsed_data['BatPowerEntLaden'] = 0

    def correct_data(self):
        if self.parsed_data['acPower'] <= 0.001:
            self.parsed_data['AktHomeConsumptionSolar'] = 0
            self.parsed_data['AktHomeConsumptionBat'] = 0  # Vermutlich nicht nötig, da noch nicht gesehen...
            self.parsed_data['AktHomeConsumption'] = self.parsed_data['AktHomeConsumptionGrid']
        elif self.parsed_data['dcPowerPV'] <= 0.001:
            self.parsed_data['AktHomeConsumptionSolar'] = 0
            self.parsed_data['AktHomeConsumption'] = \
                self.parsed_data['AktHomeConsumptionGrid'] + self.parsed_data['AktHomeConsumptionBat']

        # manchmal ist AktHomeConsumptionSolar negativ...wird hier korrigiert
        if self.parsed_data['AktHomeConsumptionSolar'] < 0 or self.parsed_data['AktHomeConsumptionBat'] < 0 or \
                self.parsed_data['AktHomeConsumption'] < 0 or self.parsed_data['AktHomeConsumptionGrid'] < 0:
            if self.parsed_data['AktHomeConsumptionSolar'] < 0:
                logger.info('AktHomeConsumptionSolar is negative')
                self.parsed_data['AktHomeConsumptionSolar'] = 0
            if self.parsed_data['AktHomeConsumptionBat'] < 0:
                logger.info('AktHomeConsumptionBat is negative')
                self.parsed_data['AktHomeConsumptionBat'] = 0
            if self.parsed_data['AktHomeConsumptionGrid'] < 0:
                logger.info('AktHomeConsumptionGrid is negative')
                self.parsed_data['AktHomeConsumptionGrid'] = 0

            self.parsed_data['AktHomeConsumption'] = \
                self.parsed_data['AktHomeConsumptionSolar'] + self.parsed_data['AktHomeConsumptionBat'] + \
                self.parsed_data['AktHomeConsumptionGrid']

        # Correction of loading battery by grid(Ausgleichsladung)
        if self.parsed_data['BatCurrentDir'] == 0 and \
                self.parsed_data['BatPowerLaden'] > self.parsed_data['AktHomeConsumptionGrid'] and \
                self.parsed_data['dcPowerPV'] < 1:
            logger.info('Bat is loaded by Grid - assigning loading to AktHomeConsumptionGrid/AktHomeConsumption')
            self.parsed_data['AktHomeConsumptionGrid'] += self.parsed_data['BatPowerLaden']

            self.parsed_data['AktHomeConsumption'] += self.parsed_data['BatPowerLaden']

        if self.parsed_data['acPower'] > 0.001:
            self.parsed_data['EinspeisenPower'] = self.parsed_data['acPower'] - \
                                                  self.parsed_data['AktHomeConsumptionSolar'] - \
                                                  self.parsed_data['AktHomeConsumptionBat']
        else:
            self.parsed_data['EinspeisenPower'] = 0

        if self.parsed_data['EinspeisenPower'] < 0:
            self.parsed_data['EinspeisenPower'] = 0

    def add_batLadenFrei(self):
        begrenzung = 0.99 * self.configuration.getfloat(self.name, 'LeistungsBegrenzung')
        self.parsed_data['BatLaden_Frei'] = 0
        if self.parsed_data['BatPowerLaden'] > 0.1:
            if self.parsed_data['EinspeisenPower'] > begrenzung:
                self.parsed_data['BatLaden_Frei'] = self.parsed_data['BatPowerLaden']
            elif (self.parsed_data['BatPowerLaden'] + self.parsed_data['EinspeisenPower']) > begrenzung:
                self.parsed_data['BatLaden_Frei'] = self.parsed_data['BatPowerLaden'] + \
                                                    self.parsed_data['EinspeisenPower'] - begrenzung


if __name__ == "__main__":
    logger.error('logger file needs to be run directly')
