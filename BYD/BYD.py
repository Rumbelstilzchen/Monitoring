# -*- coding: utf-8 -*-

from datetime import datetime
import pytz
from requests.auth import HTTPBasicAuth
import requests
import re
from lxml import etree
from retry import retry
import logging
from base_monitoring.monitorin_base_class import Base_Parser


logger = logging.getLogger(__name__)


def check_values_empty(dict_data):
    for value in dict_data.values():
        if value == "":
            return True
    return False


class BYD(Base_Parser):
    name = 'BYD'

    def __init__(self, config):
        super().__init__()
        self.configuration = config
        self.timestamp = None
        # self.time_zone = 'Europe/Berlin'
        self.time_zone = 'UTC'
        self.tz = pytz.timezone(self.time_zone)
        self.site_struct = {
            'StatisticInformation': {'Laden_kWh': ['Total Charge Energy:', float],
                                     'EntLaden_kWh': ['Total Discharge Energy:', float],
                                     'CycleCounts': ['Total Cycle Counts:', int]},
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
        self.load_data_fromurl()
        self.add_extra_entries()
        return self.parsed_data

    @retry(tries=2, delay=0)
    def load_data_fromurl(self):
        data = {}
        my_session = requests.Session()
        authentication = HTTPBasicAuth(self.configuration[self.name]['username'],
                                       self.configuration[self.name]['password'])
        self.timestamp = datetime.now(self.tz)
        for key, value in self.site_struct.items():
            url = "http://" + self.configuration[self.name]['IPAdresse'] + "/asp/" + key + ".asp"
            r4 = my_session.get(url, auth=authentication)
            if r4.status_code == 200:
                page = r4.text
                page = page.replace('><input readonly="readonly" type="text" value=', '>')
                page = page.replace('&#8451', '')
                page = page.replace(' id="1"', '')

                xml_doc = etree.HTML(page)
                # soup = BeautifulSoup(page, 'html.parser')
                # soup_ele = soup.body
                for entry, searchstring in value.items():
                    # temp2 = soup_ele.find("td", text=searchstring).find_next_sibling("td").text
                    temp = xml_doc.xpath('string(//td[.="'+searchstring[0]+'"]/following-sibling::*[1][name()="td"])')
                    data[entry] = searchstring[1](
                        re.findall(r"[-+]? ?[.]?\d+[.]?\d*(?: ?[eE] ?[-+]?\d*)?", temp)[0]
                    )
                    # data[entry] = temp.split()[0]
            if check_values_empty(data):
                logger.error('empty strings were found')
                raise ValueError('empty strings were found')
        self.parsed_data = data

    def add_extra_entries(self):
        self.parsed_data['time_sec'] = int(self.timestamp.timestamp())
        self.parsed_data['TIMESTAMP'] = datetime.fromtimestamp(self.parsed_data['time_sec'], self.tz).strftime(
            '%Y-%m-%d %H:%M:%S')


if __name__ == "__main__":
    logger.error('logger file needs to be run directly')
    parser = BYD
    import configparser

    configuration = configparser.ConfigParser()
    configuration.sections()
    configuration.read(r'..\config.ini')
    parser_init = parser(configuration)
    parser_init.collect_data()
