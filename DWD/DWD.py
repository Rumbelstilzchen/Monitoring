# -*- coding: utf-8 -*-

import logging
import os
from math import exp
from collections import OrderedDict
import pytz
import zipfile
import urllib.request
import shutil
from datetime import datetime
import xml.etree.ElementTree as ET
import numpy as np

logger = logging.getLogger(__name__)


def check_values_empty(dict_data):
    for value in dict_data.values():
        if value == "":
            return True
    return False


class DWD:
    def __init__(self, config):
        self.configuration = config
        self.timestamp = None
        self.parsed_data = OrderedDict()
        self.tz = pytz.timezone('Europe/Berlin')
        self.names_space = {'dwd': 'https://opendata.dwd.de/weather/lib/pointforecast_dwd_extension_V1_0.xsd',
                   'gx': 'http://www.google.com/kml/ext/2.2',
                   'kml': 'http://www.opengis.net/kml/2.2', 'atom': 'http://www.w3.org/2005/Atom',
                   'xal': 'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'}
        self.station_IDs = self.configuration['DWD']['DWD_station_IDs'].split(',')
        self.station_link = self.configuration['DWD']['DWD_link']
        self.dict_IDs = {
            # 'TN': 'Tn',  # Minimum temperature - within the last 12 hours
            # 'TX': 'Tx',      # Maximum temperature - within the last 12 hours
            'TTT': ['Temperature', 1, -273.15],  # Temperature 2m above surface
            'SunD1': ['SS1' , 1, 0],
            'Nh': ['Bewoelkung_H', 1, 0],  # High cloud cover (>7 km)
            'Nm': ['Bewoelkung_M', 1, 0],  # Midlevel cloud cover (2-7 km) (%)
            'Nl': ['Bewoelkung_L', 1, 0],  # Low cloud cover (lower than 2 km) (%)
            # 'RR3c': 'RR%6',   # Total precipitation during the last hour (kg/m2),
            # 'R130': 'RR6',    # Probability of precipitation > 3.0 mm during the last hour
            'DD': ['Wind_direction', 1, 0],  # 0°..360°, Wind direction
            'FF': ['Windgeschw', 1, 0],  # Wind speed (m/s)
            'FX1': ['Boeen', 1, 0],  # Maximum wind gust within the last hour (m/s)
            # 'FXh25': 'fx6',   # Probability of wind gusts >= 25kn within the last 12 hours (% 0..100)
            # 'FXh40': 'fx9',   # Probability of wind gusts >= 40kn within the last 12 hours
            # 'FXh55': 'fx11',  # Probability of wind gusts >= 55kn within the last 12 hours
            'PPPP': ['Luftdruck', 0.01, 0], # Surface pressure, reduced (Pa)
            # 'N': 'N',
            'Td': ['Td', 1, -273.15],
            # 'SS24': 'SS24',
            'Rad1h': ['Rad1h', 1, 0],  # kJ/m2
        }
        # self.collect_data()


    @staticmethod
    def getHumidity(T, TD):
        try:
            RH = 100 * (exp((17.625 * TD) / (243.04 + TD)) / exp((17.625 * T) / (243.04 + T)))
        except Exception:
            RH = '---'
        return RH

    def collect_data(self):
        self.parse_data()
        self.average_parsed_data()
        self.add_timesec()
        return self.parsed_data

    def add_timesec(self):
        self.parsed_data['time_sec'] = [int(x.timestamp()) for x in self.parsed_data['TIMESTAMP']]
        self.parsed_data['TIMESTAMP'] = [datetime.fromtimestamp(x, self.tz).strftime('%Y-%m-%d %H:%M:%S') for x in self.parsed_data['time_sec']]

    def parse_data(self):
        self.parsed_data = {}
        self.parsed_data['TIMESTAMP'] = []
        for item in self.dict_IDs.values():
            self.parsed_data[item[0]] = []
        self.parsed_data['Humidity'] = []
        for station_ID in self.station_IDs:
            link = self.configuration['DWD']['DWD_link'].replace('[station_ID]', station_ID)
            self.load_data(link)

    def average_parsed_data(self):
        temp_data = OrderedDict()

        # Handling the fact that not all downloaded date starts with the same timestamp - using only those stations that
        # have the same common start time
        first_times_list = np.array([x[0] for x in self.parsed_data['TIMESTAMP']])
        (unique_times, counts_times) = np.unique(first_times_list, return_counts=True)
        timestamp_with_max_number = unique_times[np.argmax(counts_times)]
        item_selector_for_identical_times = (first_times_list == timestamp_with_max_number)

        temp_data['TIMESTAMP'] = self.parsed_data['TIMESTAMP'][
            next(i for i, v in enumerate(item_selector_for_identical_times) if v)]
        for item_key in self.parsed_data.keys():
            if item_key is not 'TIMESTAMP':
                value = np.mean(np.array(self.parsed_data[item_key], dtype=np.float)[item_selector_for_identical_times],
                                axis=0)
                temp_data[item_key] = getattr(value, "tolist", lambda: value)()
        self.parsed_data = temp_data

    def load_data(self, link):
        temp_filename = 'tempfile.zip'
        # Download the file from `url` and save it locally under `self.file_name`:
        with urllib.request.urlopen(link) as response, open(temp_filename, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)

        with zipfile.ZipFile(temp_filename, "r") as zip_ref:
            Myzipfilename = (zip_ref.namelist())
            Myzipfilename = str(Myzipfilename[0])
            with zip_ref.open(Myzipfilename) as file:
                tree = ET.parse(file)

        if os.path.exists(temp_filename):
            os.remove(temp_filename)
        else:
            logger.debug("The file does not exist")

        root = tree.getroot()

        timestamps = root.findall(
            'kml:Document/kml:ExtendedData/dwd:ProductDefinition/dwd:ForecastTimeSteps/dwd:TimeStep', self.names_space)
        timevalue = []
        for child in timestamps:
            timevalue.append(pytz.timezone('UTC').localize(datetime.strptime(child.text, '%Y-%m-%dT%H:%M:%S.%fZ')))

        output_data = OrderedDict()

        self.parsed_data['TIMESTAMP'].append(timevalue)
        for elem in tree.findall('./kml:Document/kml:Placemark', self.names_space):  # Position us at the Placemark
            # print ("SUCERJH ", sucher)
            # print ("Elemente ", elem.tag, elem.attrib, elem.text)
            mylocation = elem.find('kml:name', self.names_space).text  # Look for the station Number

            # Here we pull the required data out of the xml file
            # if (self.mylocation == self.mystation):
            # print ("meine location", self.mylocation)
            myforecastdata = elem.find('kml:ExtendedData', self.names_space)
            for elem in myforecastdata:
                # We may get the following strings and are only interested in the right hand quoted property name WPcd1:
                # {'{https://opendata.dwd.de/weather/lib/pointforecast_dwd_extension_V1_0.xsd}elementName': 'WPcd1'}
                trash = str(elem.attrib)
                trash1, mosmix_element = trash.split("': '")
                mosmix_element, trash = mosmix_element.split("'}")
                # -------------------------------------------------------------
                # Currently looking at the following key Data:
                # Looking for the following mosmix_elements
                # FF : Wind Speed            [m/s]
                # Rad1h : Global irridance   [kJ/m²]
                # TTT : Temperature 2m above ground [Kelvin]
                # PPPP : Pressure reduced    [Pa]
                # -------------------------------------------------------------
                if mosmix_element in self.dict_IDs.keys():
                    self.parsed_data[self.dict_IDs[mosmix_element][0]].append([float(x)*self.dict_IDs[mosmix_element][1]+self.dict_IDs[mosmix_element][2] for x in elem[0].text.split()])
        Humidity_List = []
        for index, TD in enumerate(self.parsed_data['Td'][-1]):
            Humidity_List.append(self.getHumidity(self.parsed_data['Temperature'][-1][index], TD))
        self.parsed_data['Humidity'].append(Humidity_List)

