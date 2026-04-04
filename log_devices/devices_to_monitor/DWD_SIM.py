# -*- coding: utf-8 -*-

import logging
import os
from math import exp
import pytz
from retry import retry
import zipfile
import urllib.request
import shutil
from datetime import datetime, timedelta
import xml.etree.ElementTree as x_ET
import numpy as np
import pandas as pd
import pvlib
import json
from pvlib.pvsystem import PVSystem
from pvlib.location import Location
from pvlib.modelchain import ModelChain
from pvlib.temperature import TEMPERATURE_MODEL_PARAMETERS
from base_classes.monitorin_base_class import Base_Parser
from base_classes.mqtt import MQTTBase

logger = logging.getLogger(__name__)


def check_values_empty(dict_data):
    for value in dict_data.values():
        if value == "":
            return True
    return False


name_configsection_SIM = "PVLib_Settings"


def convert_to_float(input_string):
    try:
        return float(input_string)
    except Exception:
        # logger.info(
        #     f"string {input_string} could not be converted to float. Used nan instead"
        # )
        return np.nan


class DWD_SIM(Base_Parser):
    name = "DWD_SIM"

    names_space = {
        "dwd": "https://opendata.dwd.de/weather/lib/pointforecast_dwd_extension_V1_0.xsd",
        "gx": "http://www.google.com/kml/ext/2.2",
        "kml": "http://www.opengis.net/kml/2.2",
        "atom": "http://www.w3.org/2005/Atom",
        "xal": "urn:oasis:names:tc:ciq:xsdschema:xAL:2.0",
    }

    dict_IDs = {
        # 'TN': 'Tn',  # Minimum temperature - within the last 12 hours
        # 'TX': 'Tx',      # Maximum temperature - within the last 12 hours
        "TTT": ["Temperature", 1, -273.15],  # Temperature 2m above surface
        "SunD1": ["SS1", 1, 0],
        "Nh": ["Bewoelkung_H", 1, 0],  # High cloud cover (>7 km)
        "Nm": ["Bewoelkung_M", 1, 0],  # Midlevel cloud cover (2-7 km) (%)
        "Nl": ["Bewoelkung_L", 1, 0],  # Low cloud cover (lower than 2 km) (%)
        "N": ["Bewoelkung", 1, 0],  # Total cloud cover (%)
        "Neff": ["Bewoelkung_eff", 1, 0],  # Effective cloud cover (%)
        # 'RR3c': 'RR%6',   # Total precipitation during the last hour (kg/m2),
        # 'R130': 'RR6',    # Probability of precipitation > 3.0 mm during the last hour
        "DD": ["Wind_direction", 1, 0],  # 0°..360°, Wind direction
        "FF": ["Windgeschw", 1, 0],  # Wind speed (m/s)
        "FX1": ["Boeen", 1, 0],  # Maximum wind gust within the last hour (m/s)
        # 'FXh25': 'fx6',   # Probability of wind gusts >= 25kn within the last 12 hours (% 0..100)
        # 'FXh40': 'fx9',   # Probability of wind gusts >= 40kn within the last 12 hours
        # 'FXh55': 'fx11',  # Probability of wind gusts >= 55kn within the last 12 hours
        "PPPP": ["Luftdruck", 0.01, 0],  # Surface pressure, reduced (Pa)
        "VV": ["Visibility", 1, 0],  # Visibility (m)
        # 'N': 'N',
        "Td": ["Td", 1, -273.15],
        # 'SS24': 'SS24',
        "Rad1h": ["Rad1h", 1, 0],  # kJ/m2
        "RRS1c": ["SnowRainEquiv", 1, 0],  # kg/m"
    }

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
        self.SIM_class = SIM(config)
        self.station_IDs = self.configuration[self.name]["DWD_station_IDs"].split(",")
        self.station_link = self.configuration[self.name]["DWD_link"]

        self.mqtt = None
        try:
            self.mqtt = MQTTBase(self.name, self.configuration[self.name].get('mqtt', None), self.suppress_zeros)
        except Exception as e:
            logger.exception("Cannot connect to MQTT")
            raise e



    @staticmethod
    def getHumidity(T, TD):
        try:
            RH = 100 * (
                exp((17.625 * TD) / (243.04 + TD)) / exp((17.625 * T) / (243.04 + T))
            )
        except Exception:
            RH = "---"
        return RH

    def collect_data(self):
        """Collecting Data

        :return:
        """
        self.parse_data()
        self.average_parsed_data()
        self.add_timesec()
        if name_configsection_SIM in self.configuration:
            self.parsed_data = self.SIM_class.simulate_values(self.parsed_data)

        self.prepare_mqtt_data_and_send()

        return self.parsed_data

    def prepare_mqtt_data_and_send(self):
        if self.mqtt.mqtt_client is None:
            return
        PandasDF = pd.DataFrame.from_dict(self.parsed_data)
        PandasDF["TIMESTAMP"] = pd.to_datetime(
            PandasDF["TIMESTAMP"], format="%Y-%m-%d %H:%M:%S", utc=True
        )
        PandasDF.set_index("TIMESTAMP", inplace=True)
        now = datetime.now(tz=pytz.timezone("UTC"))
        PandasDF = PandasDF.loc[
            (PandasDF.index >= now) & (PandasDF.index.date <= now.date())
        ]
        # current_hour_fraction = (PandasDF['time_sec'][0]-now.timestamp())/3600
        if PandasDF.shape[0] >= 2:
            self.mqtt_data = {
                # "time_sec": int(PandasDF["time_sec"][0]),
                "time_sec": PandasDF["time_sec"].iloc[0].item(),
                "TIMESTAMP": f"{PandasDF.index[0]}",
                # *current_hour_fraction + PandasDF['DCSim'][1]*(1-current_hour_fraction)),
                # "hour_this": int(PandasDF["DCSim"][0]),
                "hour_this": PandasDF["DCSim"].iloc[0].item(),
                # *current_hour_fraction + PandasDF['DCSim'][1]*(1-current_hour_fraction)),
                # "hour_next": int(PandasDF["DCSim"][1]),
                "hour_next": PandasDF["DCSim"].iloc[1].item(),
                # -PandasDF['DCSim'][0]*(1-current_hour_fraction)),
                # "remaining_day": int(PandasDF["DCSim"].sum()),
                "remaining_day": PandasDF["DCSim"].sum().item(),
            }
            self.mqtt.send_data(self.mqtt_data)


    def add_timesec(self):
        """Add UNIX timestamp

        :return:
        """
        self.parsed_data["time_sec"] = [
            int(x.timestamp()) for x in self.parsed_data["TIMESTAMP"]
        ]
        self.parsed_data["TIMESTAMP"] = [
            datetime.fromtimestamp(x, self.tz).strftime("%Y-%m-%d %H:%M:%S")
            for x in self.parsed_data["time_sec"]
        ]

    def parse_data(self):
        """

        :return:
        """
        self.parsed_data = {"TIMESTAMP": [], "Humidity": []}
        for item in self.dict_IDs.values():
            self.parsed_data[item[0]] = []
        for station_ID in self.station_IDs:
            link = self.configuration[self.name]["DWD_link"].replace(
                "[station_ID]", station_ID
            )
            self.load_data(link)

    def average_parsed_data(self):
        """

        :return:
        """
        temp_data = {}

        # Handling the fact that not all downloaded date starts with the same timestamp - using only those stations that
        # have the same common start time
        first_times_list = np.array([x[0] for x in self.parsed_data["TIMESTAMP"]])
        (unique_times, counts_times) = np.unique(first_times_list, return_counts=True)
        timestamp_with_max_number = unique_times[np.argmax(counts_times)]
        item_selector_for_identical_times = (
            first_times_list == timestamp_with_max_number
        )

        temp_data["TIMESTAMP"] = self.parsed_data["TIMESTAMP"][
            next(i for i, v in enumerate(item_selector_for_identical_times) if v)
        ]
        is_nan_map = None
        for item_key in self.parsed_data.keys():
            if item_key != "TIMESTAMP":
                value = np.nanmean(
                    np.array(self.parsed_data[item_key], dtype=float)[
                        item_selector_for_identical_times
                    ],
                    axis=0,
                )
                # temp_data[item_key] = getattr(value, "tolist", lambda: value)()
                temp_data[item_key] = value
                if is_nan_map is None:
                    is_nan_map = np.isnan(value)
                is_nan_map = np.logical_or(is_nan_map, np.isnan(value))
        valid_map = np.logical_not(is_nan_map)
        self.parsed_data = {
            key: v_item[valid_map].tolist()
            for key, v_item in temp_data.items()
            if key != "TIMESTAMP"
        }
        self.parsed_data["TIMESTAMP"] = [
            i for i, v in zip(temp_data["TIMESTAMP"], valid_map.tolist()) if v
        ]
        # self.parsed_data = temp_data

    @retry(tries=2, delay=0)
    def load_data(self, link):
        """Load data from link

        :param str link: Provide Link
        :return:
        """
        temp_filename = "tempfile_%s.zip" % self.name
        # Download the file from `url` and save it locally under `self.file_name`:
        with urllib.request.urlopen(link, timeout=self.timeout) as response, open(
            temp_filename, "wb"
        ) as out_file:
            shutil.copyfileobj(response, out_file)

        with zipfile.ZipFile(temp_filename, "r") as zip_ref:
            Myzipfilename = zip_ref.namelist()
            Myzipfilename = str(Myzipfilename[0])
            with zip_ref.open(Myzipfilename) as file:
                tree = x_ET.parse(file)

        if os.path.exists(temp_filename):
            os.remove(temp_filename)
        else:
            logger.debug("The file does not exist")

        root = tree.getroot()

        timestamps = root.findall(
            "kml:Document/kml:ExtendedData/dwd:ProductDefinition/dwd:ForecastTimeSteps/dwd:TimeStep",
            self.names_space,
        )
        timevalue = []
        for child in timestamps:
            timevalue.append(
                pytz.timezone("UTC").localize(
                    datetime.strptime(child.text, "%Y-%m-%dT%H:%M:%S.%fZ")
                )
            )

        nan_at_data = False
        self.parsed_data["TIMESTAMP"].append(timevalue)
        for elem in tree.findall(
            "./kml:Document/kml:Placemark", self.names_space
        ):  # Position us at the Placemark
            myforecastdata = elem.find("kml:ExtendedData", self.names_space)
            for elem_2 in myforecastdata:
                # We may get the following strings and are only interested in the right hand quoted property name WPcd1:
                # {'{https://opendata.dwd.de/weather/lib/pointforecast_dwd_extension_V1_0.xsd}elementName': 'WPcd1'}
                trash = str(elem_2.attrib)
                trash1, mosmix_element = trash.split("': '")
                mosmix_element, trash = mosmix_element.split("'}")
                if mosmix_element in self.dict_IDs.keys():
                    try:
                        self.parsed_data[self.dict_IDs[mosmix_element][0]].append(
                            [
                                convert_to_float(x) * self.dict_IDs[mosmix_element][1]
                                + self.dict_IDs[mosmix_element][2]
                                for x in elem_2[0].text.split()
                            ]
                        )
                    except Exception as e:
                        logger.exception(
                            f"cannot add {mosmix_element}\n\t{elem_2[0].text}\n\t{link}"
                        )
                        raise e
                    if not nan_at_data:
                        nan_at_data = np.any(
                            np.isnan(
                                self.parsed_data[self.dict_IDs[mosmix_element][0]][-1]
                            )
                        )
        Humidity_List = []
        for index, TD in enumerate(self.parsed_data["Td"][-1]):
            Humidity_List.append(
                self.getHumidity(self.parsed_data["Temperature"][-1][index], TD)
            )
        self.parsed_data["Humidity"].append(Humidity_List)
        if nan_at_data:
            logger.info(f"found nan at parsing of {link}")


class SIM:
    def __init__(self, config):
        self.config = config
        self.longitude = self.config.getfloat(
            name_configsection_SIM, "Longitude"
        )
        self.latitude = self.config.getfloat(
            name_configsection_SIM, "Latitude"
        )
        self.altitude = self.config.getfloat(
            name_configsection_SIM, "Altitude"
        )
        self.elevation = self.config.getfloat(
            name_configsection_SIM, "Elevation"
        )
        self.azimuth = self.config.getfloat(name_configsection_SIM, "Azimuth")
        self.min_cos_zenith = self.config.getfloat(
            name_configsection_SIM, "min_cos_zenith"
        )
        self.NumPanels = self.config.getint(
            name_configsection_SIM, "NumPanels"
        )
        self.NumStrings = self.config.getint(
            name_configsection_SIM, "NumStrings"
        )
        self.albedo = self.config.getfloat(name_configsection_SIM, "Albedo")
        self.temperature_model = self.config.get(
            name_configsection_SIM, "TEMPERATURE_MODEL"
        )
        self.inverter = self.config.get(
            name_configsection_SIM, "InverterName"
        )
        self.module = self.config.get(name_configsection_SIM, "ModuleName")
        self.module_eff = self.config.getfloat(
            name_configsection_SIM, "ModulEfficiency"
        )
        self.TemperatureOffset = self.config.getfloat(
            name_configsection_SIM, "TemperatureOffset"
        )

        self.temperature_model_parameters = TEMPERATURE_MODEL_PARAMETERS["sapm"][
            self.temperature_model
        ]

        if self.module in pvlib.pvsystem.retrieve_sam("cecmod").keys():
            self.sandia_module = pvlib.pvsystem.retrieve_sam("cecmod")[self.module]
        else:
            if "own_moduls_file" in self.config:
                filename = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", self.config["own_moduls_file"])
                self.sandia_module = pvlib.pvsystem.retrieve_sam(path=filename)[self.module]
            else:
                raise ValueError(f"Module {self.module} not found in pvlib cecmod and no own_moduls_file provided in config")

        if self.inverter in pvlib.pvsystem.retrieve_sam("cecinverter").keys():
            self.cec_inverter = pvlib.pvsystem.retrieve_sam("cecinverter")[
                self.inverter
            ]
        else:
            if "own_inverter_file" in self.config:
                filename = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config",
                                        self.config["own_inverter_file"])
                self.cec_inverter = pvlib.pvsystem.retrieve_sam(path=filename)[self.inverter]
            else:
                raise ValueError(f"Inverter {self.inverter} not found in pvlib cecinverter and no own_inverter_file provided in config")


        self.pvliblocation = Location(
            latitude=self.latitude,
            longitude=self.longitude,
            tz="UTC",
            altitude=self.altitude,
        )

        self.solarsystem = PVSystem(
            surface_tilt=self.elevation,
            surface_azimuth=self.azimuth,
            module=self.sandia_module,
            inverter=self.cec_inverter,
            module_parameters=self.sandia_module,
            inverter_parameters=self.cec_inverter,
            albedo=self.albedo,
            modules_per_string=self.NumPanels,
            racking_model="open_rack",
            temperature_model_parameters=self.temperature_model_parameters,
            strings_per_inverter=self.NumStrings,
        )

        self.ModelChain = ModelChain(
            self.solarsystem,
            self.pvliblocation,
            aoi_model="no_loss",
            spectral_model="no_loss",
            # orientation_strategy=None, spectral_model="no_loss",
            temperature_model="sapm",
        )
        # self.ModelChain = ModelChain.with_sapm(self.solarsystem, self.pvliblocation,
        #                              orientation_strategy="None")

        self.simplemultiplicationfactor = (
            self.module_eff * self.NumPanels * self.NumStrings * self.sandia_module.A_c
        )

    def simulate_values(self, parsed_data):
        PandasDF = pd.DataFrame(data=parsed_data)
        PandasDF.Rad1h = PandasDF.Rad1h.astype(
            float
        )  # Need to ensure we get a float value from Rad1h

        PandasDF.Windgeschw = PandasDF.Windgeschw.astype(float)
        PandasDF.Luftdruck = PandasDF.Luftdruck.astype(float)
        PandasDF.Temperature = (
            PandasDF.Temperature.astype(float) + self.TemperatureOffset
        )
        PandasDF["Rad1wh"] = (
            PandasDF.Rad1h / 3.6
        )  # Converting from KJ/m² to Wh/m² -and adding as new column Rad1wh

        local_timestamp = pd.DatetimeIndex(
            pd.to_datetime(pd.Series(PandasDF.TIMESTAMP), utc=True)
            - timedelta(hours=0, minutes=30)
        )
        PandasDF.index = local_timestamp

        # =============================================================================
        # STARTING  SOLAR POSITION AND ATMOSPHERIC MODELING
        # =============================================================================
        solpos = pvlib.solarposition.get_solarposition(
            time=local_timestamp,
            latitude=self.latitude,
            longitude=self.longitude,
            altitude=self.altitude,
        )

        # DNI and DHI calculation from GHI data
        DNI = pvlib.irradiance.disc(
            ghi=PandasDF.Rad1wh,
            solar_zenith=solpos.zenith,
            datetime_or_doy=local_timestamp,
            pressure=PandasDF.Luftdruck * 100,
            min_cos_zenith=self.min_cos_zenith,
        )
        DHI = pvlib.irradiance.erbs(
            ghi=PandasDF.Rad1wh,
            zenith=solpos.zenith,
            datetime_or_doy=local_timestamp,
            min_cos_zenith=self.min_cos_zenith,
        )

        dataheader = {
            "ghi": PandasDF.Rad1wh,
            "dni": DNI.dni,
            "dhi": DHI.dhi,
            "temp_air": PandasDF.Temperature,
            "wind_speed": PandasDF.Windgeschw,
        }
        mc_weather = pd.DataFrame(data=dataheader)
        mc_weather.index = local_timestamp
        # Simulating the PV system using pvlib modelchain

        # pvlib has changed their APIs between versions ... need to deal with it ...:
        self.ModelChain.run_model(mc_weather)

        # parsed_data["ACSim"] = list(self.ModelChain.results.ac)
        parsed_data["ACSim"] = self.ModelChain.results.ac.tolist()
        # parsed_data["CellTempSim"] = list(self.ModelChain.results.cell_temperature)
        parsed_data["CellTempSim"] = self.ModelChain.results.cell_temperature.tolist()
        # modelchain provides DC data too - but no doc was found for the other values below
        # i_sc        v_oc          i_mp        v_mp         p_mp           i_x          i_xx
        # parsed_data["DCSim"] = list(self.ModelChain.results.dc.p_mp)
        parsed_data["DCSim"] = self.ModelChain.results.dc.p_mp.tolist()
        # parsed_data["VmpSIM"] = list(self.ModelChain.results.dc.v_mp)
        parsed_data["VmpSIM"] = self.ModelChain.results.dc.v_mp.tolist()
        # parsed_data["ImpSIM"] = list(self.ModelChain.results.dc.i_mp / self.NumStrings)
        parsed_data["ImpSIM"] = (
            self.ModelChain.results.dc.i_mp / self.NumStrings
        ).tolist()

        # parsed_data["Rad1Energy"] = list(self.simplemultiplicationfactor * PandasDF.Rad1wh)
        parsed_data["Rad1Energy"] = (
            self.simplemultiplicationfactor * PandasDF.Rad1wh
        ).tolist()
        # parsed_data["Rad1wh"] = list(PandasDF.Rad1wh)
        parsed_data["Rad1wh"] = PandasDF.Rad1wh.tolist()

        return parsed_data


def simulate_old_data():
    parser = DWD_SIM

    from db_wrapper.mysql import db_write
    import configparser

    configuration = configparser.ConfigParser()
    configuration.sections()
    configuration.read(r"..\config.ini")

    parser_init = parser(configuration)

    MYSQL_config = {
        "mysql_host": configuration["MYSQL"]["mysql_host"],
        "mysql_port": configuration.getint("MYSQL", "mysql_port"),
        "mysql_username": configuration[parser.name]["mysql_username"],
        "mysql_pw": configuration[parser.name]["mysql_pw"],
        "mysql_DB": configuration[parser.name]["mysql_DB"],
        "mysql_table": configuration[parser.name]["mysql_tablename"],
        "time_zone": parser_init.time_zone,
    }
    if "mysql_type" in configuration[parser.name].keys():
        MYSQL_config["StatementType"] = configuration[parser.name]["mysql_type"]
    MYsqlConnection = db_write(MYSQL_config)

    # get old_data
    with MYsqlConnection.connection.cursor() as cursor:
        cursor.execute(
            ("select * FROM %s;" % configuration[parser.name]["mysql_tablename"])
        )
        # cursor.execute("select * FROM DWD_Daten;")
        record = cursor.fetchall()
        names = [x[0] for x in cursor.description]

    parsed_data = {}
    for index, key in enumerate(names):
        if key == "TIMESTAMP":
            parsed_data[key] = [str(x[index]) for x in record]
        else:
            parsed_data[key] = [x[index] for x in record]

    logging_data = parser_init.SIM_class.simulate_values(parsed_data)
    MYsqlConnection.write_dict_data(logging_data)


if __name__ == "__main__":
    simulate_old_data()
