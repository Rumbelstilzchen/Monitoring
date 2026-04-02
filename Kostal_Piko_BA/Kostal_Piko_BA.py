# -*- coding: utf-8 -*-

import json
import base64
import hashlib
import pickle
from datetime import datetime
import pytz
from retry import retry
import logging
import urllib3
from base_monitoring.monitorin_base_class import Base_Parser
import paho.mqtt.client as mqtt  # import the client1

from itertools import islice

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


def login_to_kostal(
    http: urllib3.poolmanager, base_url: str, username="pvserver", password="pvwr"
):
    # Login-URL
    login_url = f"{base_url}/api/login.json"
    try:
        # Login-Request durchführen
        # response = http.request(
        #     "GET",
        #     login_url,
        # ).json()
        response = json.loads(
            http.request(
                "GET",
                login_url,
            ).data.decode("utf-8")
        )

        session_id = response.get("session").get("sessionId")
        salt = response.get("salt")

        combined = password + salt  # Reihenfolge wie im JS
        hash_value = hashlib.sha1(combined.encode("utf-8")).digest()
        pwh = base64.b64encode(hash_value).decode()

        login_data = {
            "mode": 1,
            "userId": username,
            "pwh": pwh,
        }
        response = http.request(
            "post",
            f"{login_url}?sessionId={session_id}",
            json=login_data,
        )

        # Prüfen ob Login erfolgreich
        if (
            response.status == 200
            and json.loads(response.data.decode("utf-8"))
            .get("session")
            .get("roleId", 0)
            > 0
        ):
            logger.info("Login erfolgreich")
            return session_id
        else:
            logger.warning(f"Login fehlgeschlagen: {response.status}")
            return None
    except Exception as e:
        logger.error(f"Login failed: {e}")
        return None


class Kostal_Piko_BA(Base_Parser):
    name = "Kostal_Piko_BA"

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
        self.dict_dxsID_openWB = {
            67109379: "GridPowerL1",
            67109635: "GridPowerL2",
            67109891: "GridPowerL3",
            67109377: "GridCurrentL1",
            67109633: "GridCurrentL2",
            67109889: "GridCurrentL3",
            83887106: "AktHomeConsumptionL1",
            83887362: "AktHomeConsumptionL2",
            83887618: "AktHomeConsumptionL3",
        }
        self.dict_dxsID = {
            # 167772417: 'Analog1',
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
            # 201327114: 'UseBattery',
            33556226: "BatVoltage",
            33556238: "BatCurrent",
            33556230: "BatCurrentDir",
            33556228: "ChargeCycles",
            33556227: "BatTemperature",
            33556229: "BatStateOfCharge",
            83886336: "AktHomeConsumptionSolar",
            83886592: "AktHomeConsumptionBat",
            83886848: "AktHomeConsumptionGrid",
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
            83887872: "AktHomeConsumption",
            33555203: "dc1Power",
            33555459: "dc2Power",
            # 33555715: 'dc3Power',
            33556736: "dcPowerPV",
            67109120: "acPower",
            16780032: "operatingStatus",
            67110400: "GridFreq",
            67110656: "GridCosPhi",
            67110144: "GridLimitation",
            # 67109379: 'GridPowerL1',
            # 67109635: 'GridPowerL2',
            # 67109891: 'GridPowerL3',
            67109378: "GridVoltageL1",
            67109634: "GridVoltageL2",
            67109890: "GridVoltageL3",
            # 67109377: 'GridCurrentL1',
            # 67109633: 'GridCurrentL2',
            # 67109889: 'GridCurrentL3',
            # 83887106: 'AktHomeConsumptionL1',
            # 83887362: 'AktHomeConsumptionL2',
            # 83887618: 'AktHomeConsumptionL3',
            33555202: "dc1Voltage",
            33555201: "dc1Current",
            33555458: "dc2Voltage",
            33555457: "dc2Current",
            # 33555714: 'dc3Voltage',
            # 33555713: 'dc3Current',
            # 83888128: 'ownConsumption',
        }

        self.nr_of_decimal_for_round["BatCurrentDir"] = 0
        self.average_ignores = [
            "TIMESTAMP",
            "time_sec",
            "operatingStatus",
            "ChargeCycles",
            "MaxVolPos",
            "MinVolPos",
            "MaxTempPos",
            "MinTempPos",
            "CycleCounts",
        ]
        self.suppress_zeros = [
            "BatVoltage",
            "BatCurrent",
            "BatTemperature",
            "BatStateOfCharge",
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
                "evu_exported": 0,
                "evu_imported": 0,
                "pv_exported": 0,
                "bat_exported": 0,
                "bat_imported": 0,
                # '': 0,
                # '': 0,
                # '': 0,
            }
        self.mqtt_client = None
        self.mqtt_topic = ""
        self.mqtt_openwb_client = None
        self.mqtt_openwb_topics = None
        try:
            self.connect_mqtt()
        except Exception as e:
            logger.exception("Cannot connect to MQTT")
            raise e

        # Auth-Header erzeugen
        self.username = self.configuration[self.name].get("username", "pvserver")
        self.password = self.configuration[self.name].get("password", "pvwr")
        self.session_id = None
        self.login_needed = True

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
                    f"equipment/{Kostal_Piko_BA.name}/connection",
                    "online",
                    qos=1,
                    retain=True,
                )

            self.mqtt_client.username_pw_set(
                self.configuration.get(self.name, "MQTT_user"),
                self.configuration.get(self.name, "MQTT_PW"),
            )
            self.mqtt_client.tls_set("ca.crt")
            # self.mqtt_client.tls_insecure_set(False)
            self.mqtt_client.on_connect = on_connect
            self.mqtt_client.connect(
                host=self.configuration.get(self.name, "MQTT_broker_ip"),
                port=self.configuration.getint(self.name, "MQTT_broker_port"),
            )
            self.mqtt_client.loop_start()
            # self.mqtt_client.publish(f"equipment/{self.name}/status", 'online', qos=1, retain=True)

        if "MQTT_openwb_broker_ip" in self.configuration[self.name]:
            self.mqtt_openwb_topics = {}
            if "MQTT_openwb_topic_evu" in self.configuration[self.name]:
                self.mqtt_openwb_topics["evu"] = self.configuration.get(
                    self.name, "MQTT_openwb_topic_evu"
                )
            if "MQTT_openwb_topic_wr" in self.configuration[self.name]:
                self.mqtt_openwb_topics["wr"] = self.configuration.get(
                    self.name, "MQTT_openwb_topic_wr"
                )
            if "MQTT_openwb_topic_bat" in self.configuration[self.name]:
                self.mqtt_openwb_topics["bat"] = self.configuration.get(
                    self.name, "MQTT_openwb_topic_bat"
                )

            self.mqtt_openwb_client = mqtt.Client(
                mqtt.CallbackAPIVersion.VERSION2,
                client_id=f"{self.name}_openWB_logger",
                clean_session=False,
                protocol=4,
            )  # create new instance
            self.mqtt_openwb_client.will_set(
                f"equipment/{self.name}_openWB/connection",
                "offline",
                qos=1,
                retain=True,
            )

            def on_connect_openWB(client, userdata, flags, reason_code, properties):
                logger.info(f"Connecting - setting online status - rc: {reason_code}")
                client.publish(
                    f"equipment/{Kostal_Piko_BA.name}_openWB/connection",
                    "online",
                    qos=1,
                    retain=True,
                )

            self.mqtt_openwb_client.username_pw_set(
                self.configuration.get(self.name, "MQTT_openwb_user"),
                self.configuration.get(self.name, "MQTT_openwb_PW"),
            )
            self.mqtt_openwb_client.tls_set("ca.crt")
            # self.mqtt_client.tls_insecure_set(False)
            self.mqtt_openwb_client.on_connect = on_connect_openWB
            self.mqtt_openwb_client.connect(
                host=self.configuration.get(self.name, "MQTT_openwb_broker_ip"),
                port=self.configuration.getint(self.name, "MQTT_openwb_broker_port"),
            )
            self.mqtt_openwb_client.loop_start()
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
        if self.mqtt_openwb_client is not None:
            try:
                self.mqtt_openwb_client.publish(
                    f"equipment/{self.name}_openWB/connection",
                    "offline",
                    qos=1,
                    retain=True,
                )
                logger.info('MQTT "offline"-status for openwb was set')
                self.mqtt_client.loop_stop()
            except Exception:
                logger.exception('MQTT failed to set "offline"-status for openwb')

    def collect_data(self):
        self.parsed_data = self.load_data_fromurl()
        self.add_extra_entries()
        self.correct_data()
        self.add_batLadenFrei()
        self.accumulate_data()
        if self.mqtt_client is not None:
            self.mqtt_data.update(
                {
                    key: value
                    for key, value in self.parsed_data.items()
                    if key not in self.suppress_zeros
                }
            )
            if self.parsed_data["dcPowerPV"] < 10:
                pv_production = 0
            else:
                pv_production = (
                    self.parsed_data["BatPowerLaden"]
                    + self.parsed_data["EinspeisenPower"]
                    + self.parsed_data["AktHomeConsumptionSolar"]
                )
            self.mqtt_data["pv_export_virt"] = pv_production
            self.mqtt_data.update(self.accumulated_data)
            self.send_mqtt_data()
        if self.mqtt_openwb_client is not None:
            self.send_mqtt_data_openwb()
        return self.parsed_data

    def set_averages(self, averaged_data):
        if self.mqtt_client is not None:
            self.mqtt_data.update(
                {
                    key: value
                    for key, value in averaged_data.items()
                    if key in self.suppress_zeros
                }
            )
            self.send_mqtt_data()

    def accumulate_data(self):
        today = self.timestamp.astimezone(tz=pytz.timezone("Europe/Berlin")).date()
        if today > self.last_day:
            self.last_day = today
            logger.info("New day reset accumulated data")
            self.accumulated_data = {key: 0 for key in self.accumulated_data}
        self.accumulated_data["evu_exported"] += (
            self.parsed_data["EinspeisenPower"] * self.refreshrate / 3600
        )
        self.accumulated_data["evu_imported"] += (
            self.parsed_data["AktHomeConsumptionGrid"] * self.refreshrate / 3600
        )

        if self.parsed_data["dcPowerPV"] < 10:
            pv_production = 0
        else:
            pv_production = (
                self.parsed_data["BatPowerLaden"]
                + self.parsed_data["EinspeisenPower"]
                + self.parsed_data["AktHomeConsumptionSolar"]
            )
            # pv_production = (
            #     self.parsed_data["acPower"]
            # )
        self.accumulated_data["pv_exported"] += pv_production * self.refreshrate / 3600

        if self.parsed_data["BatCurrentDir"] == 0:
            self.accumulated_data["bat_imported"] += (
                self.parsed_data["BatPowerLaden"] * self.refreshrate / 3600
            )
        else:
            if self.parsed_data["dcPowerPV"] < 10:
                self.accumulated_data["bat_exported"] += (
                    (
                        self.parsed_data["AktHomeConsumptionBat"]
                        + self.parsed_data["EinspeisenPower"]
                    )
                    * self.refreshrate
                    / 3600
                )
            else:
                self.accumulated_data["bat_exported"] += (
                    self.parsed_data["AktHomeConsumptionBat"] * self.refreshrate / 3600
                )

    def send_mqtt_data_openwb(self):
        try:
            if not self.mqtt_openwb_client.is_connected():
                self.mqtt_openwb_client.reconnect()
            list_for_send = []
            extra_data = self.load_data_fromurl(self.dict_dxsID_openWB)
            for data_type, global_topic in self.mqtt_openwb_topics.items():
                if data_type == "evu":
                    list_for_send.append(
                        (
                            f"{global_topic}exported",
                            self.accumulated_data["evu_exported"],
                        )
                    )
                    list_for_send.append(
                        (
                            f"{global_topic}imported",
                            self.accumulated_data["evu_imported"],
                        )
                    )
                    if self.parsed_data["EinspeisenPower"] > 0:
                        gridPower = -self.parsed_data["EinspeisenPower"]
                    else:
                        gridPower = self.parsed_data["AktHomeConsumptionGrid"]
                    list_for_send.append((f"{global_topic}power", gridPower))
                    list_for_send.append(
                        (
                            f"{global_topic}powers",
                            str(
                                [
                                    extra_data[f"AktHomeConsumptionL{phase+1}"]
                                    - extra_data[f"GridPowerL{phase+1}"]
                                    for phase in range(3)
                                ]
                            ),
                        )
                    )
                    list_for_send.append(
                        (f"{global_topic}frequency", self.parsed_data["GridFreq"])
                    )
                    list_for_send.append(
                        (
                            f"{global_topic}voltages",
                            str(
                                [
                                    self.parsed_data[f"GridVoltageL{phase+1}"]
                                    for phase in range(3)
                                ]
                            ),
                        )
                    )

                if data_type == "wr":
                    list_for_send.append(
                        (
                            f"{global_topic}exported",
                            self.accumulated_data["pv_exported"],
                        )
                    )

                if data_type == "bat":
                    if self.parsed_data["BatCurrentDir"] == 0:
                        list_for_send.append(
                            (f"{global_topic}power", self.parsed_data["BatPowerLaden"])
                        )
                    else:
                        if self.parsed_data["dcPowerPV"] < 10:
                            list_for_send.append(
                                (
                                    f"{global_topic}power",
                                    -self.parsed_data["AktHomeConsumptionBat"]
                                    - self.parsed_data["EinspeisenPower"],
                                )
                            )
                        else:
                            list_for_send.append(
                                (
                                    f"{global_topic}power",
                                    -self.parsed_data["AktHomeConsumptionBat"],
                                )
                            )
                    list_for_send.append(
                        (
                            f"{global_topic}exported",
                            self.accumulated_data["bat_exported"],
                        )
                    )
                    list_for_send.append(
                        (
                            f"{global_topic}imported",
                            self.accumulated_data["bat_imported"],
                        )
                    )

                    list_for_send.append(
                        (f"{global_topic}soc", self.parsed_data["BatStateOfCharge"])
                    )
                    if self.parsed_data["BatStateOfCharge"] == 0:
                        return
            # logger.info(self.accumulated_data)
            for address, value in list_for_send:
                self.mqtt_openwb_client.publish(address, value)
        except Exception:
            logger.exception("Error Sending date to mqtt_client - no retry")

    def send_mqtt_data(self):
        try:
            if not self.mqtt_client.is_connected():
                self.mqtt_client.reconnect()
            json_data = json.dumps(self.mqtt_data)
            self.mqtt_client.publish(self.mqtt_topic, json_data)
        except Exception:
            logger.exception("Error Sending date to mqtt_client - no retry")

    @staticmethod
    def reformat_data(input_dict, dictionary):
        # output = {}
        # for x in input_dict:
        #    output[dictionary[x['dxsId']]] = x['value']
        output = {dictionary[x["dxsId"]]: x["value"] for x in input_dict}
        return output

    @retry(tries=2, delay=0)
    def load_data_fromurl(self, dxs_set=None):
        data = {}
        base_url = (
            "http://" + self.configuration[self.name]["IPAdresse"] + "/api/dxs.json?"
        )
        self.timestamp = datetime.now(self.tz)
        if dxs_set is None:
            dxs_set = self.dict_dxsID
        if self.http is None:
            timeout = urllib3.Timeout(self.timeout)
            self.http = urllib3.PoolManager(timeout=timeout)
        for dxs_set_sub in chunks(dxs_set, 15):

            if self.login_needed or self.session_id is None:
                self.session_id = login_to_kostal(
                    self.http,
                    "http://" + self.configuration[self.name]["IPAdresse"],
                    self.username,
                    self.password,
                )
                if self.session_id is None:
                    logger.error("Login failed")
                    self.session_id = 0
                else:
                    self.login_needed = False

            dxs_string = "&dxsEntries=".join(f"{v}" for v in dxs_set_sub)

            json_url = self.http.request(
                "GET",
                f"{base_url}dxsEntries={dxs_string}&sessionId={self.session_id}",
                retries=False,
            )
            url_response = json.loads(json_url.data.decode("utf-8"))
            # url_response = json_url.json()
            data.update(self.reformat_data(url_response["dxsEntries"], dxs_set))
            if url_response.get("session").get("roleId") == 0:
                self.login_needed = True
                logger.warning("Session expired, login needed again")
            # logger.debug(f"dxsEntries={dxs_string}")
            # with urllib.request.urlopen(base_url + 'dxsEntries=' + dxs_string, timeout=1) as json_url:
            #     url_response = json.loads(json_url.read().decode('utf8'))
            #     data.update(self.reformat_data(url_response['dxsEntries'], dxs_set))
            if check_values_empty(data):
                logger.error("empty strings were found")
                raise ValueError("empty strings were found")
        return data

    def add_extra_entries(self):
        self.parsed_data["time_sec"] = int(self.timestamp.timestamp())
        self.parsed_data["TIMESTAMP"] = datetime.fromtimestamp(
            self.parsed_data["time_sec"], self.tz
        ).strftime("%Y-%m-%d %H:%M:%S")
        if self.parsed_data["BatCurrentDir"] == 0:
            self.parsed_data["BatPowerLaden"] = (
                self.parsed_data["BatCurrent"] * self.parsed_data["BatVoltage"]
            )
        else:
            self.parsed_data["BatPowerLaden"] = 0

        if self.parsed_data["BatCurrentDir"] == 1:
            self.parsed_data["BatPowerEntLaden"] = (
                self.parsed_data["BatCurrent"] * self.parsed_data["BatVoltage"]
            )
        else:
            self.parsed_data["BatPowerEntLaden"] = 0

    def correct_data(self):
        if self.parsed_data["acPower"] <= 0.001:
            self.parsed_data["AktHomeConsumptionSolar"] = 0
            self.parsed_data["AktHomeConsumptionBat"] = (
                0  # Vermutlich nicht nötig, da noch nicht gesehen...
            )
            self.parsed_data["AktHomeConsumption"] = self.parsed_data[
                "AktHomeConsumptionGrid"
            ]
        elif self.parsed_data["dcPowerPV"] < 10:
            self.parsed_data["AktHomeConsumptionSolar"] = 0
            self.parsed_data["AktHomeConsumption"] = (
                self.parsed_data["AktHomeConsumptionGrid"]
                + self.parsed_data["AktHomeConsumptionBat"]
            )

        # manchmal ist AktHomeConsumptionSolar negativ...wird hier korrigiert
        if (
            self.parsed_data["AktHomeConsumptionSolar"] < 0
            or self.parsed_data["AktHomeConsumptionBat"] < 0
            or self.parsed_data["AktHomeConsumption"] < 0
            or self.parsed_data["AktHomeConsumptionGrid"] < 0
        ):
            if self.parsed_data["AktHomeConsumptionSolar"] < 0:
                logger.info("AktHomeConsumptionSolar is negative")
                self.parsed_data["AktHomeConsumptionSolar"] = 0
            if self.parsed_data["AktHomeConsumptionBat"] < 0:
                logger.info("AktHomeConsumptionBat is negative")
                self.parsed_data["AktHomeConsumptionBat"] = 0
            if self.parsed_data["AktHomeConsumptionGrid"] < 0:
                logger.info("AktHomeConsumptionGrid is negative")
                self.parsed_data["AktHomeConsumptionGrid"] = 0

            self.parsed_data["AktHomeConsumption"] = (
                self.parsed_data["AktHomeConsumptionSolar"]
                + self.parsed_data["AktHomeConsumptionBat"]
                + self.parsed_data["AktHomeConsumptionGrid"]
            )

        # Correction of loading battery by grid (Ausgleichsladung)
        if (
            self.parsed_data["BatCurrentDir"] == 0
            and self.parsed_data["BatPowerLaden"]
            > self.parsed_data["AktHomeConsumptionGrid"]
            and self.parsed_data["dcPowerPV"] < 10
        ):
            logger.info(
                "Bat is loaded by Grid - assigning loading to AktHomeConsumptionGrid/AktHomeConsumption"
            )
            self.parsed_data["AktHomeConsumptionGrid"] += self.parsed_data[
                "BatPowerLaden"
            ]

            self.parsed_data["AktHomeConsumption"] += self.parsed_data["BatPowerLaden"]

        if self.parsed_data["acPower"] > 0.001:
            self.parsed_data["EinspeisenPower"] = (
                self.parsed_data["acPower"]
                - self.parsed_data["AktHomeConsumptionSolar"]
                - self.parsed_data["AktHomeConsumptionBat"]
            )
        else:
            self.parsed_data["EinspeisenPower"] = 0

        if self.parsed_data["EinspeisenPower"] < 0:
            self.parsed_data["EinspeisenPower"] = 0

    def add_batLadenFrei(self):
        begrenzung = 0.99 * self.configuration.getfloat(
            self.name, "LeistungsBegrenzung"
        )
        self.parsed_data["BatLaden_Frei"] = 0
        if self.parsed_data["BatPowerLaden"] > 0.1:
            if self.parsed_data["EinspeisenPower"] > begrenzung:
                self.parsed_data["BatLaden_Frei"] = self.parsed_data["BatPowerLaden"]
            elif (
                self.parsed_data["BatPowerLaden"] + self.parsed_data["EinspeisenPower"]
            ) > begrenzung:
                self.parsed_data["BatLaden_Frei"] = (
                    self.parsed_data["BatPowerLaden"]
                    + self.parsed_data["EinspeisenPower"]
                    - begrenzung
                )


if __name__ == "__main__":
    logger.error("logger file needs to be run directly")
