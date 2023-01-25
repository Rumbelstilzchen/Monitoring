# -*- coding: utf-8 -*-

from datetime import datetime
import pytz
import socket
import struct
from retry import retry
import logging
# from urllib.request import urlopen
import urllib3
import re
from base_monitoring.monitorin_base_class import Base_Parser


logger = logging.getLogger(__name__)


def check_values_empty(dict_data):
    for value in dict_data.values():
        if value == "":
            return True
    return False


class Luxtronik(Base_Parser):
    name = 'Luxtronik'

    def __init__(self, config):
        super().__init__()
        self.configuration = config
        self.hostHeatpump = self.configuration[self.name]['host']
        self.portHeatpump = self.configuration.getint(self.name, 'port')
        if self.configuration.has_option(self.name, 'host_HK'):
            self.tasmota = self.configuration[self.name]['host_HK']
        else:
            self.tasmota = None
        self.http = None
        self.timestamp = None
        # self.time_zone = 'Europe/Berlin'
        self.time_zone = 'UTC'
        self.tz = pytz.timezone(self.time_zone)
        self._socket = None
        self.tasmota_regex = r"[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?"

        # self.IDs_all = ['?', '?', '?', '?', '?', '?', '?', '?', '?', '?', 'Temperatur_TVL', 'Temperatur_TRL', 'Sollwert_TRL_HZ', 'Temperatur_TRL_ext', 'Temperatur_THG', 'Temperatur_TA', 'Mitteltemperatur', 'Temperatur_TBW', 'Einst_BWS_akt', 'Temperatur_TWE', 'Temperatur_TWA', 'Temperatur_TFB1', 'Sollwert_TVL_MK1', 'Temperatur_RFV', 'Temperatur_TFB2', 'Sollwert_TVL_MK2', 'Temperatur_TSK', 'Temperatur_TSS', 'Temperatur_TEE', 'ASDin', 'BWTin', 'EVUin', 'HDin', 'MOTin', 'NDin', 'PEXin', 'SWTin', 'AVout', 'BUPout', 'HUPout', 'MA1out', 'MZ1out', 'VENout', 'VBOout', 'VD1out', 'VD2out', 'ZIPout', 'ZUPout', 'ZW1out', 'ZW2SSTout', 'ZW3SSTout', 'FP2out', 'SLPout', 'SUPout', 'MZ2out', 'MA2out', 'Zaehler_BetrZeitVD1', 'Zaehler_BetrZeitImpVD1', 'Zaehler_BetrZeitVD2', 'Zaehler_BetrZeitImpVD2', 'Zaehler_BetrZeitZWE1', 'Zaehler_BetrZeitZWE2', 'Zaehler_BetrZeitZWE3', 'Zaehler_BetrZeitWP', 'Zaehler_BetrZeitHz', 'Zaehler_BetrZeitBW', 'Zaehler_BetrZeitKue', 'Time_WPein_akt', 'Time_ZWE1_akt', 'Time_ZWE2_akt', 'Timer_EinschVerz', 'Time_SSPAUS_akt', 'Time_SSPEIN_akt', 'Time_VDStd_akt', 'Time_HRM_akt', 'Time_HRW_akt', 'Time_LGS_akt', 'Time_SBW_akt', 'Code_WP_akt', 'BIV_Stufe_akt', 'WP_BZ_akt', 'SoftStand1', 'SoftStand2', 'SoftStand3', 'SoftStand4', 'SoftStand5', 'SoftStand6', 'SoftStand7', 'SoftStand8', 'SoftStand9', 'SoftStand10', 'AdresseIP_akt', 'SubNetMask_akt', 'Add_Broadcast', 'Add_StdGateway', 'ERROR_Time0', 'ERROR_Time1', 'ERROR_Time2', 'ERROR_Time3', 'ERROR_Time4', 'ERROR_Nr0', 'ERROR_Nr1', 'ERROR_Nr2', 'ERROR_Nr3', 'ERROR_Nr4', 'AnzahlFehlerInSpeicher', 'Switchoff_file_Nr0', 'Switchoff_file_Nr1', 'Switchoff_file_Nr2', 'Switchoff_file_Nr3', 'Switchoff_file_Nr4', 'Switchoff_file_Time0', 'Switchoff_file_Time1', 'Switchoff_file_Time2', 'Switchoff_file_Time3', 'Switchoff_file_Time4', 'Comfort_exists', 'HauptMenuStatus_Zeile1', 'HauptMenuStatus_Zeile2', 'HauptMenuStatus_Zeile3', 'HauptMenuStatus_Zeit', 'HauptMenuAHP_Stufe', 'HauptMenuAHP_Temp', 'HauptMenuAHP_Zeit', 'SH_BWW', 'SH_HZ', 'SH_MK1', 'SH_MK2', 'Einst_Kurzprogramm', 'StatusSlave_1', 'StatusSlave_2', 'StatusSlave_3', 'StatusSlave_4', 'StatusSlave_5', 'AktuelleTimeStamp', 'SH_MK3', 'Sollwert_TVL_MK3', 'Temperatur_TFB3', 'MZ3out', 'MA3out', 'FP3out', 'Time_AbtIn', 'Temperatur_RFV2', 'Temperatur_RFV3', 'SH_SW', 'Zaehler_BetrZeitSW', 'FreigabKuehl', 'AnalogIn', 'SonderZeichen', 'SH_ZIP', 'WebsrvProgrammWerteBeobachten', 'WMZ_Heizung', 'WMZ_Brauchwasser', 'WMZ_Schwimmbad', 'WMZ_Seit', 'WMZ_Durchfluss', 'AnalogOut1', 'AnalogOut2', 'Time_Heissgas', 'Temp_Lueftung_Zuluft', 'Temp_Lueftung_Abluft', 'Zaehler_BetrZeitSolar', 'AnalogOut3', 'AnalogOut4', 'Out_VZU', 'Out_VAB', 'Out_VSK', 'Out_FRH', 'AnalogIn2', 'AnalogIn3', 'SAXin', 'SPLin', 'Compact_exists', 'Durchfluss_WQ', 'LIN_exists', 'LIN_ANSAUG_VERDAMPFER', 'LIN_ANSAUG_VERDICHTER', 'LIN_VDH', 'LIN_UH', 'LIN_UH_Soll', 'LIN_HD', 'LIN_ND', 'LIN_VDH_out', 'HZIO_PWM', 'HZIO_VEN', 'HZIO_EVU2', 'HZIO_STB', 'SEC_Qh_Soll', 'SEC_Qh_Ist', 'SEC_TVL_Soll', 'SEC_Software', 'SEC_BZ', 'SEC_VWV', 'SEC_VD', 'SEC_VerdEVI', 'SEC_AnsEVI', 'SEC_UEH_EVI', 'SEC_UEH_EVI_S', 'SEC_KondTemp', 'SEC_FlussigEx', 'SEC_UK_EEV', 'SEC_EVI_Druck', 'SEC_U_Inv', 'Temperatur_THG_2', 'Temperatur_TWE_2', 'LIN_ANSAUG_VERDAMPFER_2', 'LIN_ANSAUG_VERDICHTER_2', 'LIN_VDH_2', 'LIN_UH_2', 'LIN_UH_Soll_2', 'LIN_HD_2', 'LIN_ND_2', 'HDin_2', 'AVout_2', 'VBOout_2', 'VD1out_2', 'LIN_VDH_out_2', 'Switchoff2_Nr0', 'Switchoff2_Nr1', 'Switchoff2_Nr2', 'Switchoff2_Nr3', 'Switchoff2_Nr4', 'Switchoff2_Time0', 'Switchoff2_Time1', 'Switchoff2_Time2', 'Switchoff2_Time3', 'Switchoff2_Time4', 'RBE_RT_Ist', 'RBE_RT_Soll', 'Temp_BW_oben', 'Code_WP_akt_2', 'Freq_VD', 'LIN_Temp_ND', 'LIN_Temp_HD', 'Abtauwunsch', 'Abtauwunsch_2', 'Freq_Soll', 'Freq_Min', 'Freq_Max', 'VBO_Soll', 'VBO_Ist', 'HZUP_PWM', 'HZUP_Soll', 'HZUP_Ist', 'Temperatur_VLMax', 'Temperatur_VLMax_2', 'SEC_EVi', 'SEC_EEV', 'Time_ZWE3_akt']

        self.IDs = {  # id of readback: ['name in DB', Scaling factor, number of digits]
            10: ['flowTemperature', 0.1, 1],
            11: ['returnTemperature', 0.1, 1],
            12: ['returnTemperatureTarget', 0.1, 1],
            13: ['returnTemperatureExtern', 0.1, 1],
            15: ['ambientTemperature', 0.1, 1],
            16: ['averageAmbientTemperature', 0.1, 1],
            17: ['hotWaterTemperature', 0.1, 1],
            18: ['hotWaterTemperatureTarget', 0.1, 1],
            19: ["heatSourceIN", 0.1, 1],
            20: ["heatSourceOUT", 0.1, 1],
            44: ['compressor1', None],
            39: ['heatingSystemCircPump', None],
            38: ['hotWaterSwitchingValve', None],
            56: ["counterHoursVD1", 1.0/3600, 2],
            57: ["counterStartsVD1", None],
            63: ['counterHoursHeatpump', 1.0/3600, 2],
            64: ['counterHoursHeating', 1.0/3600, 2],
            65: ['counterHoursHotWater', 1.0/3600, 2],
            151: ["counterHeatQHeating", 0.1, 1],
            152: ["counterHeatQHotWater", 0.1, 1],
            155: ["flowRate", None],
        }
        self.average_ignores = [
            'TIMESTAMP',
            'time_sec',
            'operatingStatus',
            'ChargeCycles',
            'BatCurrentDir',
            'MaxVolPos',
            'MinVolPos',
            'MaxTempPos',
            'MinTempPos',
            'CycleCounts'
        ]

    def collect_data(self):
        self.load_data()
        self.add_extra_entries()
        if self.tasmota is not None:
            self.read_temp_sensor()
        return self.parsed_data

    def _read_from_socket(self):
        data_raw = []
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((self.hostHeatpump, self.portHeatpump))
        self._socket.sendall(struct.pack(">ii", 3004, 0))
        cmd = struct.unpack(">i", self._socket.recv(4))[0]
        logger.debug("Command %s", cmd)
        stat = struct.unpack(">i", self._socket.recv(4))[0]
        logger.debug("Stat %s", stat)
        length = struct.unpack(">i", self._socket.recv(4))[0]
        self.timestamp = datetime.now(self.tz)
        logger.debug("Length %s", length)
        for d in range(0, length):
            data_raw.append(struct.unpack(">i", self._socket.recv(4))[0])
        logger.debug("Read %d calculations", length)
        self._socket.close()
        logger.debug("Disconnected from Luxtronik heatpump  %s:%s", self.hostHeatpump, self.portHeatpump)
        return data_raw

    @retry(tries=2, delay=0)
    def load_data(self):
        raw_data = self._read_from_socket()
        self.parsed_data = {}
        for key, value in self.IDs.items():
            if value[0] == 'flowRate':
                flowrate = raw_data[key]
                self.parsed_data['thermalPower'] = \
                    abs(self.parsed_data['flowTemperature'] - self.parsed_data['returnTemperature']) * flowrate / 866.65
            else:
                if value[1] is not None:
                    self.parsed_data[value[0]] = round(raw_data[key] * value[1], value[2])
                else:
                    self.parsed_data[value[0]] = raw_data[key]
        self.parsed_data['counterHeatQTotal'] = \
            round(self.parsed_data['counterHeatQHeating'] + self.parsed_data['counterHeatQHotWater'], 1)

    @retry(tries=2, delay=1)
    def read_temp_sensor(self):
        link = "http://%s/?m=1" % self.tasmota
        if self.http is None:
            self.http = urllib3.PoolManager()
        f = self.http.request('GET', link, retries=False)
        myfile = f.data.decode('utf-8').split('{m}')
        # f = urlopen(link, timeout=10)
        # myfile = str(f.read()).split('{m}')
        self.parsed_data['VL_HK'] = re.findall(self.tasmota_regex, myfile[1])[0]
        self.parsed_data['RL_HK'] = re.findall(self.tasmota_regex, myfile[2])[0]

    def add_extra_entries(self):
        self.parsed_data['time_sec'] = int(self.timestamp.timestamp())
        self.parsed_data['TIMESTAMP'] = datetime.fromtimestamp(self.parsed_data['time_sec'], self.tz).strftime(
            '%Y-%m-%d %H:%M:%S')


def manual_read_and_print_data():
    parser = Luxtronik
    import configparser
    configuration = configparser.ConfigParser()
    configuration.sections()
    configuration.read(r'..\config.ini')

    parser_init = parser(configuration)

    for key, value in parser_init.collect_data().items():
        print('%s:\t%s' % (key, value))


if __name__ == "__main__":
    logger.warning('For monitoring, script needs to be run by: python monitoring_template.py Luxtronik')
    manual_read_and_print_data()
