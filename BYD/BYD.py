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


def check_values_empty(dict_data):
    for value in dict_data.values():
        if value == "":
            return True
    return False


class BYD:
    def __init__(self, config):
        self.configuration = config
        self.timestamp = None
        self.tz = pytz.timezone('Europe/Berlin')
        self.parsed_data = OrderedDict()
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
        data = OrderedDict()
        mySession = requests.Session()
        authentication = HTTPBasicAuth(self.configuration['BYD']['username'], self.configuration['BYD']['password'])
        self.timestamp = datetime.now(self.tz)
        for key, value in self.site_struct.items():
            url = "http://" + self.configuration['BYD']['IPAdresse'] + "/asp/" + key + ".asp"
            r4 = mySession.get(url, auth=authentication)
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
                    data[entry] = searchstring[1](re.findall("[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?", temp)[0])
                    # data[entry] = temp.split()[0]
            if check_values_empty(data):
                logging.error('empty strings were found')
                raise ValueError('empty strings were found')
        self.parsed_data = data

    def add_extra_entries(self):
        self.parsed_data['time_sec'] = int(self.timestamp.timestamp())
        self.parsed_data['TIMESTAMP'] = datetime.fromtimestamp(self.parsed_data['time_sec'], self.tz).strftime(
            '%Y-%m-%d %H:%M:%S')


if __name__ == "__main__":
    logging.error('logger file needs to be run directly')
