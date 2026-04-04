# -*- coding: utf-8 -*-

from datetime import datetime
import pytz
from requests.auth import HTTPBasicAuth
import requests
import re
from lxml import etree
from retry import retry
import logging
from base_classes.monitorin_base_class import Base_Parser


logger = logging.getLogger(__name__)


def check_values_empty(dict_data):
    for value in dict_data.values():
        if value == "":
            return True
    return False


class BYD(Base_Parser):
    name = 'BYD'

    influx_tags = {
        "Power_kW": (
            "power",
            float,
            {
                "measurement": "byd_battery",
                "tags": {
                    "flow_type": "dc",
                    "flow_source": "WR",
                    "flow_destination": "battery",
                    "type": "power",
                    "unit": "kW",
                    "device": "byd_battery",
                },
            },
        ),
        "Current_A": (
            "current",
            float,
            {
                "measurement": "byd_battery",
                "tags": {
                    "flow_type": "dc",
                    "flow_source": "WR",
                    "flow_destination": "battery",
                    "type": "current",
                    "unit": "A",
                    "device": "byd_battery",
                },
            },
        ),
        "PackVoltage_V": (
            "voltage",
            float,
            {
                "measurement": "byd_battery",
                "tags": {
                    "flow_type": "dc",
                    "type": "voltage",
                    "unit": "V",
                    "device": "byd_battery",
                },
            },
        ),
        "CycleCounts": (
            "cycles",
            int,
            {
                "measurement": "byd_battery",
                "tags": {"type": "cycles", "device": "byd_battery"},
            },
        ),
        "SysTemp_C": (
            "temperature",
            float,
            {
                "measurement": "byd_battery",
                "tags": {
                    "type": "temperature",
                    "unit": "°C",
                    "device": "byd_battery",
                },
            },
        ),
        "SOC": (
            "SOC",
            float,
            {
                "measurement": "byd_battery",
                "tags": {"type": "SOC", "unit": "'%'", "device": "byd_battery"},
            },
        ),
        "MaxCellTemp_C": (
            "max_temperature",
            float,
            {
                "measurement": "byd_battery",
                "tags": {
                    "type": "temperature",
                    "unit": "°C",
                    "device": "byd_battery",
                },
            },
        ),
        "MinCellTemp_C": (
            "min_temperature",
            float,
            {
                "measurement": "byd_battery",
                "tags": {
                    "type": "temperature",
                    "unit": "°C",
                    "device": "byd_battery",
                },
            },
        ),
        "MaxCellVol_V": (
            "max_voltage",
            float,
            {
                "measurement": "byd_battery",
                "tags": {
                    "flow_type": "dc",
                    "type": "voltage",
                    "unit": "V",
                    "device": "byd_battery",
                },
            },
        ),
        "MinCellVol_V": (
            "min_voltage",
            float,
            {
                "measurement": "byd_battery",
                "tags": {
                    "flow_type": "dc",
                    "type": "voltage",
                    "unit": "V",
                    "device": "byd_battery",
                },
            },
        ),
        "MaxTempPos": (
            "max_temperature",
            int,
            {
                "measurement": "byd_battery",
                "tags": {
                    "type": "position",
                    "unit": "na",
                    "device": "byd_battery",
                },
            },
        ),
        "MinTempPos": (
            "min_temperature",
            int,
            {
                "measurement": "byd_battery",
                "tags": {
                    "type": "position",
                    "unit": "na",
                    "device": "byd_battery",
                },
            },
        ),
        "MaxVolPos": (
            "max_voltage",
            int,
            {
                "measurement": "byd_battery",
                "tags": {
                    "type": "position",
                    "unit": "na",
                    "device": "byd_battery",
                },
            },
        ),
        "MinVolPos": (
            "min_voltage",
            int,
            {
                "measurement": "byd_battery",
                "tags": {
                    "type": "position",
                    "unit": "na",
                    "device": "byd_battery",
                },
            },
        ),
    }

    site_struct = {
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

    def __init__(self, config):
        super().__init__()
        self.configuration = config
        try:
            self.refreshrate = self.configuration.getint(self.name, "refreshrate")
        except Exception:
            self.refreshrate = 2
        self.timeout = max(min(10, self.refreshrate - 2), 2)
        self.timestamp = None
        # self.time_zone = 'Europe/Berlin'
        self.time_zone = 'UTC'
        self.tz = pytz.timezone(self.time_zone)
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
        # Initialize session and auth once
        self.session = requests.Session()
        # if login not provided use BYD's default credentials
        self.auth = HTTPBasicAuth(
            self.configuration[self.name].get('username','installer'),
            self.configuration[self.name].get('password', 'byd@12345')
        )
        self.base_url = f"http://{self.configuration[self.name]['IPAdresse']}/asp/"


    def collect_data(self):
        self.load_data_fromurl()
        self.add_extra_entries()
        return self.parsed_data


    def load_data_fromurl(self):
        data = {}
        self.timestamp = datetime.now(self.tz)
        for subpage, data_item_struct in self.site_struct.items():
            data.update(self._parse_page(subpage, data_item_struct))
        self.parsed_data = data

    @retry(tries=2, delay=0)
    def _parse_page(self, subpage, data_item_struct):
        data = {}
        url = f"{self.base_url}{subpage}.asp"
        r4 = self.session.get(url, auth=self.auth, timeout=self.timeout)
        r4.raise_for_status()
        page = r4.text
        page = page.replace('><input readonly="readonly" type="text" value=', '>')
        page = page.replace('&#8451', '')
        page = page.replace(' id="1"', '')

        xml_doc = etree.HTML(page)
        # soup = BeautifulSoup(page, 'html.parser')
        # soup_ele = soup.body
        for entry, searchstring in data_item_struct.items():
            # temp2 = soup_ele.find("td", text=searchstring).find_next_sibling("td").text
            temp = xml_doc.xpath('string(//td[.="' + searchstring[0] + '"]/following-sibling::*[1][name()="td"])')
            match = re.findall(r"[-+]? ?[.]?\d+[.]?\d*(?: ?[eE] ?[-+]?\d*)?", temp)[0]
            if not match:
                raise ValueError(f"No number found for {entry}")
            data[entry] = searchstring[1](match)
            # data[entry] = temp.split()[0]
        if check_values_empty(data):
            logger.error('empty strings were found')
            raise ValueError('empty strings were found')
        return data

    def add_extra_entries(self):
        self.parsed_data["time_sec"] = int(self.timestamp.timestamp())
        self.parsed_data["TIMESTAMP"] = datetime.fromtimestamp(
            self.parsed_data["time_sec"], self.tz
        ).strftime("%Y-%m-%d %H:%M:%S")


if __name__ == "__main__":
    logger.error(
        "For monitoring, script needs to be run by: python monitoring_template.py BYD"
    )
