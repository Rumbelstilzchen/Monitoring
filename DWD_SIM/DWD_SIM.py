# -*- coding: utf-8 -*-

import logging
import os
from math import exp
from collections import OrderedDict
import pytz
import zipfile
import urllib.request
import shutil
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
import numpy as np
import pandas as pd
import pvlib
from pvlib.pvsystem import PVSystem
from pvlib.location import Location
from pvlib.modelchain import ModelChain
from pvlib.temperature import TEMPERATURE_MODEL_PARAMETERS

logger = logging.getLogger(__name__)


my_inverter = {
    'Vac': 240,
    'Pso': 20,
    'Paco': 8000,
    'Pdco': 8333,
    'Vdco': 680,
    'Pnt': 10,
    'Vdcmax': 950,
    'Idcmax': 12,
    'Mppt_low': 350,
    'Mppt_high': 850,
    'CAC_Type': 'Utility Interactive',
}

my_module = {
    'alpha_sc': 0.003057,
    'beta_oc': -0.11016,
    'T_NOCT': 45,
    'gamma_r': -0.37
}


def check_values_empty(dict_data):
    for value in dict_data.values():
        if value == "":
            return True
    return False


class DWD_SIM:
    name = 'DWD_SIM'

    def __init__(self, config):
        self.configuration = config
        self.SIM_class = SIM(config)
        self.timestamp = None
        self.parsed_data = OrderedDict()
        # self.time_zone = 'Europe/Berlin'
        self.time_zone = 'UTC'
        self.tz = pytz.timezone(self.time_zone)
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
        return self.SIM_class.simulate_values(self.parsed_data)
        # return self.parsed_data

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
            if item_key != 'TIMESTAMP':
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


class SIM:
    def __init__(self, config):
        self.config = config
        self.longitude = (self.config.getfloat('SolarSystem', 'Longitude', raw=True))
        self.latitude = (self.config.getfloat('SolarSystem', 'Latitude', raw=True))
        self.altitude = (self.config.getfloat('SolarSystem', 'Altitude', raw=True))
        self.elevation = (self.config.getfloat('SolarSystem', 'Elevation', raw=True))
        self.azimuth = (self.config.getfloat('SolarSystem', 'Azimuth', raw=True))
        self.NumPanels = (self.config.getint('SolarSystem', 'NumPanels', raw=True))
        self.NumStrings = (self.config.getint('SolarSystem', 'NumStrings', raw=True))
        self.albedo = (self.config.getfloat('SolarSystem', 'Albedo', raw=True))
        self.temperature_model = (self.config.get('SolarSystem', 'TEMPERATURE_MODEL', raw=True))
        self.inverter = (self.config.get('SolarSystem', 'InverterName', raw=True))
        self.module = (self.config.get('SolarSystem', 'ModuleName', raw=True))
        self.TemperatureOffset = (self.config.getfloat('SolarSystem', 'TemperatureOffset', raw=True))





        self.temperature_model_parameters = TEMPERATURE_MODEL_PARAMETERS['sapm'][self.temperature_model]

        self.sandia_module = pvlib.pvsystem.retrieve_sam('cecmod')[self.module]
        self.sandia_module.replace(pd.Series(my_module))
        self.cec_inverter = pvlib.pvsystem.retrieve_sam('cecinverter')[self.inverter]
        self.cec_inverter.replace(pd.Series(my_inverter))

        self.pvliblocation = Location(latitude=self.latitude,
                                        longitude=self.longitude,
                                        tz="UTC",
                                        altitude=self.altitude)

        self.solarsystem = PVSystem(surface_tilt=self.elevation,
                                      surface_azimuth=self.azimuth,
                                      module=self.sandia_module,
                                      inverter=self.cec_inverter,
                                      module_parameters=self.sandia_module,
                                      inverter_parameters=self.cec_inverter,
                                      albedo=self.albedo,
                                      modules_per_string=self.NumPanels,
                                      racking_model="open_rack",
                                      temperature_model_parameters=self.temperature_model_parameters,
                                      strings_per_inverter=self.NumStrings)
        self.ModelChain = ModelChain(self.solarsystem, self.pvliblocation, aoi_model='no_loss',
                                       orientation_strategy="None", spectral_model='no_loss')

    def simulate_values(self,parsed_data):
        PandasDF = pd.DataFrame(data=parsed_data)
        PandasDF.Rad1h = PandasDF.Rad1h.astype(
            float)  # Need to ensure we get a float value from Rad1h

        PandasDF.Windgeschw = PandasDF.Windgeschw.astype(float)
        PandasDF.Luftdruck = PandasDF.Luftdruck.astype(float)
        PandasDF.Temperature = PandasDF.Temperature.astype(float) + self.TemperatureOffset
        PandasDF['Rad1wh'] = PandasDF.Rad1h / 3.6  # Converting from KJ/m² to Wh/m² -and adding as new column Rad1wh
        PandasDF['myTZtimestamp'] = pd.to_datetime(pd.Series(PandasDF.TIMESTAMP), utc=True)
        # A horrific hack to get the time series working
        # first = PandasDF.myTZtimestamp.iloc[0] - timedelta(hours=0, minutes=30)
        # last = PandasDF.myTZtimestamp.iloc[PandasDF.myTZtimestamp.index[-1]] - timedelta(hours=0, minutes=30)
        #
        # # Gathering time series from start - and end hours (240 rows):
        # local_timestamp = pd.date_range(start=first, end=last, freq='1h', tz='UTC')
        local_timestamp = pd.DatetimeIndex(pd.to_datetime(pd.Series(PandasDF.TIMESTAMP), utc=True) - timedelta(hours=0, minutes=30))


        # PandasDF['Rad1Energy'] = self.simplemultiplicationfactor * PandasDF.Rad1wh

        PandasDF.index = local_timestamp

        # Now creating list of unixtimestamps
        PandasDF['mytimestamp'] = PandasDF.time_sec

        # =============================================================================
        # STARTING  SOLAR POSITION AND ATMOSPHERIC MODELING
        # =============================================================================
        solpos = pvlib.solarposition.get_solarposition(time=local_timestamp,
                                                            latitude=self.latitude,
                                                            longitude=self.longitude,
                                                            altitude=self.altitude)

        # DNI and DHI calculation from GHI data
        DNI = pvlib.irradiance.disc(ghi=PandasDF.Rad1wh, solar_zenith=solpos.zenith,
                                         datetime_or_doy=local_timestamp,
                                         pressure=PandasDF.Luftdruck*100)
        DHI = pvlib.irradiance.erbs(ghi=PandasDF.Rad1wh, zenith=solpos.zenith,
                                         datetime_or_doy=local_timestamp)

        dataheader = {'ghi': PandasDF.Rad1wh, 'dni': DNI.dni, 'dhi': DHI.dhi,
                           'temp_air': PandasDF.Temperature, 'wind_speed': PandasDF.Windgeschw}
        mc_weather = pd.DataFrame(data=dataheader)
        mc_weather.index = local_timestamp
        # Simulating the PV system using pvlib modelchain

        # pvlib has changed their APIs between versions ... need to deal with it ...:
        self.ModelChain.run_model(mc_weather)

        parsed_data['ACSim'] = list(self.ModelChain.ac)
        parsed_data['CellTempSim'] = list(self.ModelChain.cell_temperature)
        # modelchain provides DC data too - but no doc was found for the other values below
        # i_sc        v_oc          i_mp        v_mp         p_mp           i_x          i_xx
        parsed_data['DCSim'] = list(self.ModelChain.dc.p_mp)
        parsed_data['VmpSIM'] = list(self.ModelChain.dc.v_mp)
        parsed_data['ImpSIM'] = list(self.ModelChain.dc.i_mp/2)

        return parsed_data

def simulate_old_data():
    parser = DWD_SIM

    from base_MYSQL.mysql import db_write
    import configparser
    configuration = configparser.ConfigParser()
    configuration.sections()
    configuration.read(r'..\config.ini')

    parser_init = parser(configuration)

    MYSQL_config = {
        'mysql_host': configuration['MYSQL']['mysql_host'],
        'mysql_port': configuration.getint('MYSQL', 'mysql_port'),
        'mysql_username': configuration[parser.name]['mysql_username'],
        'mysql_pw': configuration[parser.name]['mysql_pw'],
        'mysql_DB': configuration[parser.name]['mysql_DB'],
        'mysql_table': configuration[parser.name]['mysql_tablename'],
        'time_zone': parser_init.time_zone,
    }
    if 'mysql_type' in configuration[parser.name].keys():
        MYSQL_config['StatementType'] = configuration[parser.name]['mysql_type']
    MYsqlConnection = db_write(MYSQL_config)

    # get old_data
    with MYsqlConnection.connection.cursor() as cursor:
        # cursor.execute(("select * FROM %s;" % configuration[parser.name]['mysql_tablename']))
        cursor.execute("select * FROM DWD_Daten;")
        record = cursor.fetchall()
        names = [x[0] for x in cursor.description]

    parsed_data = OrderedDict()
    for index, key in enumerate(names):
        if key == 'TIMESTAMP':
            parsed_data[key] = [str(x[index]) for x in record]
        else:
            parsed_data[key] = [x[index] for x in record]

    logging_data = parser_init.SIM_class.simulate_values(parsed_data)
    mysql_status = MYsqlConnection.write_dict_data(logging_data)


if __name__ == "__main__":
    simulate_old_data()