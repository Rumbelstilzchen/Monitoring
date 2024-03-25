# -*- coding: utf-8 -*-

from datetime import datetime
import pytz
from requests.auth import HTTPBasicAuth
import requests
import re
from lxml import etree
from retry import retry
from collections import OrderedDict
import logging
from base_monitoring.monitorin_base_class import Base_Parser

logger = logging.getLogger(__name__)


def check_values_empty(dict_data):
    for value in dict_data.values():
        if value == "":
            return True
    return False


class BYD_Cell_voltage(Base_Parser):
    name = 'BYD_Cell_voltage'

    def __init__(self, config):
        super().__init__()
        self.configuration = config
        self.timestamp = None
        # self.time_zone = 'Europe/Berlin'
        self.time_zone = 'UTC'
        self.tz = pytz.timezone(self.time_zone)
        self.parsed_data = OrderedDict()
        self.basic_data_infos = {}
        self.base_site_struct = {
            'UserInfo': {'Nr_Arrays': ['Array Counts :', int],
                         'Nr_Modules': ['Series Battery Counts :', int]}}
        self.site_with_voltage_data = 'RunData'
        self.detail_struct = {
            'RunData': {'PackVoltage_V': ['PackVoltage:', float],
                        'Current_A': ['Current:', float],
                        'SOC': ['SOC:', float],
                        'SysTemp_C': ['SysTemp:', float],
                        'MaxCellTemp_C': ['MaxCellTemp:', float],
                        'MinCellTemp_C': ['MinCellTemp:', float],
                        'MaxCellVol_V': ['MaxCellVol:', float],
                        'MinCellVol_V': ['MinCellVol:', float],
                        'Power_kW': ['Power:', float],
                        'MaxVolPos': ['MaxVolPos:', int],
                        'MinVolPos': ['MinVolPos:', int],
                        'MaxTempPos': ['MaxTempPos:', int],
                        'MinTempPos': ['MinTempPos:', int]}
            }
        self.load_basicdata_fromurl()

    def collect_data(self):
        self.load_voltage_data()
        return self.parsed_data

    @retry(tries=2, delay=0)
    def load_basicdata_fromurl(self):
        data = {}
        my_session = requests.Session()
        authentication = HTTPBasicAuth(self.configuration[self.name]['username'],
                                       self.configuration[self.name]['password'])
        for key, value in self.base_site_struct.items():
            url = "http://" + self.configuration[self.name]['IPAdresse'] + "/asp/" + key + ".asp"
            r4 = my_session.get(url, auth=authentication, timeout=10)
            if r4.status_code == 200:
                page = r4.text
                page = page.replace('><input readonly="readonly" type="text" value=', '>')
                page = page.replace('&#8451', '')
                page = page.replace(' id="1"', '')

                # xml_doc = etree.HTML(page)
                # soup = BeautifulSoup(page, 'html.parser')
                # soup_ele = soup.body
                for entry, searchstring in value.items():
                    data[entry] = searchstring[1](
                        re.findall(searchstring[0]+r'.*\n.*\"text_l\">(?P<val>[0-9])</td', page)[0]
                    )
                    # data[entry] = temp.split()[0]
            if check_values_empty(data):
                logger.error('empty strings were found')
                raise ValueError('empty strings were found')
        self.basic_data_infos = data

    @retry(tries=2, delay=0)
    def load_voltage_data(self):
        data = {'time_sec': [],
                'Array': [],
                'Module': [],
                'Cell': [],
                'Voltage': [],
                }
        my_session = requests.Session()
        authentication = HTTPBasicAuth(self.configuration[self.name]['username'],
                                       self.configuration[self.name]['password'])
        self.timestamp = datetime.now(self.tz)
        for array_ind in range(self.basic_data_infos['Nr_Arrays']):
            for module_ind in range(self.basic_data_infos['Nr_Modules']):
                url2 = "http://" + self.configuration[self.name]['IPAdresse'] + "/goform/SetRunData"
                payload = {"ArrayNum": array_ind+1, "SeriesBatteryNum": module_ind+1}
                r4 = requests.post(url2, auth=authentication, data=payload)

                if r4.status_code == 200:
                    page = r4.text
                    page = page.replace('><input readonly="readonly" type="text" value=', '>')
                    page = page.replace('&#8451', '')
                    page = page.replace(' id="1"', '')

                    xml_doc = etree.HTML(page)
                    # soup = BeautifulSoup(page, 'html.parser')
                    # soup_ele = soup.body
                    for i in range(16):
                        # for entry, searchstring in value.items():
                        # temp2 = soup_ele.find("td", text=searchstring).find_next_sibling("td").text
                        searchstring = f"CellVol[{i+1}]:"
                        temp = xml_doc.xpath('string(//td[.="'+searchstring+'"]/following-sibling::*[1][name()="td"])')
                        current_data = float(
                            re.findall(r"[-+]? ?[.]?\d+[.]?\d*(?: ?[eE] ?[-+]?\d*)?", temp)[0]
                        )
                        data['time_sec'].append(self.timestamp.timestamp())
                        data['Array'].append(array_ind+1)
                        data['Module'].append(module_ind+1)
                        data['Cell'].append(i+1)
                        data['Voltage'].append(current_data)
                        # data[entry] = temp.split()[0]

        self.parsed_data = data


if __name__ == "__main__":
    logger.error('logger file needs to be run directly')
    parser = BYD_Cell_voltage
    import configparser

    configuration = configparser.ConfigParser()
    configuration.sections()
    configuration.read(r'..\config.ini')
    parser_init = parser(configuration)
    parser_init.collect_data()
