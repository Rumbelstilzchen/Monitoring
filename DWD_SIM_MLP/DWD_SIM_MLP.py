# -*- coding: utf-8 -*-

import logging
import os
from math import exp

import pandas as pd
import pytz
import zipfile
import urllib.request
import shutil
from datetime import datetime
import xml.etree.ElementTree as x_ET
import numpy as np
from base_MYSQL.mysql import db_write
from base_monitoring.monitorin_base_class import Base_Parser
from DWD_SIM.DWD_SIM import SIM
import pickle
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.neural_network import MLPRegressor
from sklearn.compose import ColumnTransformer
from sklearn.compose import TransformedTargetRegressor
from sklearn.preprocessing import SplineTransformer
# from sklearn.preprocessing import QuantileTransformer as Transformer
from sklearn.preprocessing import MinMaxScaler as Transformer
# from sklearn.preprocessing import StandardScaler as Transformer

# from keras.models import Sequential
# from keras.layers import Dense,  InputLayer

logger = logging.getLogger(__name__)


def check_values_empty(dict_data):
    for value in dict_data.values():
        if value == "":
            return True
    return False


name_configsection_SIM = 'DWD_SIM_SolarSystem'


def periodic_spline_transformer(period, n_splines=None, degree=3):
    if n_splines is None:
        n_splines = period
    n_knots = n_splines + 1  # periodic and include_bias is True
    return SplineTransformer(
        degree=degree,
        n_knots=n_knots,
        knots=np.linspace(0, period, n_knots).reshape(n_knots, 1),
        extrapolation="periodic",
        include_bias=True,
    )


class DWD_SIM_MLP(Base_Parser):
    name = 'DWD_SIM_MLP'

    current_directory = os.path.dirname(__file__)
    AI_model_path = os.path.join(current_directory, 'MLP_model.bin')
    value_list = [
        "Temperature",
        "Wind_direction",
        "Windgeschw",
        "Luftdruck",
        "Rad1h",
        "Bewoelkung_L",
        "Bewoelkung_M",
        "Bewoelkung_H",
        "SS1",
        "Humidity"
    ]

    input_scaler = [
        ("cyclic_month", periodic_spline_transformer(12, n_splines=6), ['Monat']),
        ("cyclic_hour", periodic_spline_transformer(24, n_splines=12), ['Stunde']),
        ("cyclic_Wind_direction", periodic_spline_transformer(360, n_splines=180), ["Wind_direction"]),
    ]
    # input_scaler = [
    #     ("cyclic_month", Transformer(feature_range=(-1, 1)), ['Monat']),
    #     ("cyclic_hour", Transformer(feature_range=(-1, 1)), ['Stunde']),
    #     # ("cyclic_Wind_direction", periodic_spline_transformer(360, n_splines=180), ["Wind_direction"]),
    # ]

    def __init__(self, config):
        super().__init__()
        self.configuration = config
        self.SIM_class = SIM(config)
        self.timestamp = None
        # self.time_zone = 'Europe/Berlin'
        self.time_zone = 'UTC'
        self.tz = pytz.timezone(self.time_zone)
        self.names_space = {'dwd': 'https://opendata.dwd.de/weather/lib/pointforecast_dwd_extension_V1_0.xsd',
                            'gx': 'http://www.google.com/kml/ext/2.2',
                            'kml': 'http://www.opengis.net/kml/2.2', 'atom': 'http://www.w3.org/2005/Atom',
                            'xal': 'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'}
        self.station_IDs = self.configuration[self.name]['DWD_station_IDs'].split(',')
        self.station_link = self.configuration[self.name]['DWD_link']
        self.dict_IDs = {
            # 'TN': 'Tn',  # Minimum temperature - within the last 12 hours
            # 'TX': 'Tx',      # Maximum temperature - within the last 12 hours
            'TTT': ['Temperature', 1, -273.15],  # Temperature 2m above surface
            'SunD1': ['SS1', 1, 0],
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
            'PPPP': ['Luftdruck', 0.01, 0],  # Surface pressure, reduced (Pa)
            # 'N': 'N',
            'Td': ['Td', 1, -273.15],
            # 'SS24': 'SS24',
            'Rad1h': ['Rad1h', 1, 0],  # kJ/m2
        }
        try:
            with open(self.AI_model_path, 'rb') as file:
                self.AI_model = pickle.load(file)
        except Exception:
            logger.exception('No Old Model found - initializing new one')
            # self.AI_model = MLPRegressor(hidden_layer_sizes=(500, 500, 100, 100, 50), max_iter=10000000,
            #                              warm_start=True,
            #                              n_iter_no_change=100, early_stopping=True, validation_fraction=0.2)
            # define Model
            model = MLPRegressor(hidden_layer_sizes=(500, 250, 100, 50), max_iter=10000000,
                                 warm_start=True,
                                 n_iter_no_change=500, early_stopping=True, validation_fraction=0.2)
            # define transform
            transformer = ColumnTransformer(
                transformers=self.input_scaler,
                remainder=Transformer()
            )
            # define pipeline
            pipeline = Pipeline(steps=[('t', transformer), ('m', model)])
            self.AI_model = TransformedTargetRegressor(pipeline, transformer=Transformer())

            self.train_model(update_history=True)
        # self.collect_data()

    def AI_convert_dict_to_scaled_numpy(self, data_set):
        logging_data_numpy = np.zeros((len(data_set['time_sec'])))
        # Years
        logging_data_numpy = np.vstack((logging_data_numpy, [float(f[0:4]) for f in data_set['TIMESTAMP']]))
        # Month
        logging_data_numpy = np.vstack((logging_data_numpy, [float(f[5:7]) for f in data_set['TIMESTAMP']]))
        # hours = np.array([int(f[11:13]) for f in data_set['TIMESTAMP']])
        logging_data_numpy = np.vstack((logging_data_numpy, [float(f[11:13]) for f in data_set['TIMESTAMP']]))
        # Temperatur
        for key in self.value_list:
            logging_data_numpy = np.vstack((logging_data_numpy, data_set[key]))

        logging_data_numpy = logging_data_numpy.T[:, 1:]
        return logging_data_numpy

    def AI_predict_values(self, data_set):
        column_names = ['Jahr', 'Monat', 'Stunde']
        column_names.extend(self.value_list)
        logging_data_pandas = pd.DataFrame(self.AI_convert_dict_to_scaled_numpy(data_set), columns=column_names)
        prediction = np.squeeze(self.AI_model.predict(logging_data_pandas))
        prediction[np.where(np.array(data_set['Rad1h']) < 0.1)] = 0
        prediction[np.where(prediction < 0)] = 0
        prediction = np.array(prediction, dtype=float)

        # data_set['DC_AI'] = getattr(prediction, "tolist", lambda: prediction)()
        data_set['DC_AI'] = prediction.tolist()
        return data_set

    @staticmethod
    def getHumidity(T, TD):
        try:
            RH = 100 * (exp((17.625 * TD) / (243.04 + TD)) / exp((17.625 * T) / (243.04 + T)))
        except Exception:
            RH = '---'
        return RH

    def collect_data(self):
        """Collecting Data

        :return:
        """
        self.parse_data()
        self.average_parsed_data()
        self.add_timesec()
        if name_configsection_SIM in self.configuration.sections():
            self.parsed_data = self.SIM_class.simulate_values(self.parsed_data)
        self.parsed_data = self.AI_predict_values(self.parsed_data)
        return self.parsed_data

    def add_timesec(self):
        """Add UNIX timestamp

        :return:
        """
        self.parsed_data['time_sec'] = [int(x.timestamp()) for x in self.parsed_data['TIMESTAMP']]
        self.parsed_data['TIMESTAMP'] = \
            [datetime.fromtimestamp(x, self.tz).strftime('%Y-%m-%d %H:%M:%S') for x in self.parsed_data['time_sec']]

    def parse_data(self):
        """

        :return:
        """
        self.parsed_data = {'TIMESTAMP': [],
                            'Humidity': []}
        for item in self.dict_IDs.values():
            self.parsed_data[item[0]] = []
        for station_ID in self.station_IDs:
            link = self.configuration[self.name]['DWD_link'].replace('[station_ID]', station_ID)
            self.load_data(link)

    def average_parsed_data(self):
        """

        :return:
        """
        temp_data = {}

        # Handling the fact that not all downloaded date starts with the same timestamp - using only those stations that
        # have the same common start time
        first_times_list = np.array([x[0] for x in self.parsed_data['TIMESTAMP']])
        (unique_times, counts_times) = np.unique(first_times_list, return_counts=True)
        timestamp_with_max_number = unique_times[np.argmax(counts_times)]
        item_selector_for_identical_times = (first_times_list == timestamp_with_max_number)

        temp_data['TIMESTAMP'] = self.parsed_data['TIMESTAMP'][
            next(i_index for i_index, v in enumerate(item_selector_for_identical_times) if v)]
        for item_key in self.parsed_data.keys():
            if item_key != 'TIMESTAMP':
                value = np.mean(np.array(self.parsed_data[item_key], dtype=np.float)[item_selector_for_identical_times],
                                axis=0)
                temp_data[item_key] = getattr(value, "tolist", lambda: value)()
        self.parsed_data = temp_data

    def load_data(self, link):
        """Load data from link

        :param str link: Provide Link
        :return:
        """
        temp_filename = 'tempfile_%s.zip' % self.name
        # Download the file from `url` and save it locally under `self.file_name`:
        with urllib.request.urlopen(link) as response, open(temp_filename, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)

        with zipfile.ZipFile(temp_filename, "r") as zip_ref:
            Myzipfilename = (zip_ref.namelist())
            Myzipfilename = str(Myzipfilename[0])
            with zip_ref.open(Myzipfilename) as file:
                tree = x_ET.parse(file)

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

        self.parsed_data['TIMESTAMP'].append(timevalue)
        for elem in tree.findall('./kml:Document/kml:Placemark', self.names_space):  # Position us at the Placemark
            myforecastdata = elem.find('kml:ExtendedData', self.names_space)
            for elem_2 in myforecastdata:
                # We may get the following strings and are only interested in the right hand quoted property name WPcd1:
                # {'{https://opendata.dwd.de/weather/lib/pointforecast_dwd_extension_V1_0.xsd}elementName': 'WPcd1'}
                trash = str(elem_2.attrib)
                trash1, mosmix_element = trash.split("': '")
                mosmix_element, trash = mosmix_element.split("'}")
                if mosmix_element in self.dict_IDs.keys():
                    self.parsed_data[self.dict_IDs[mosmix_element][0]].append(
                        [
                            float(x) * self.dict_IDs[mosmix_element][1] + self.dict_IDs[mosmix_element][2]
                            for x in elem_2[0].text.split()
                        ]
                    )
        Humidity_List = []
        for index, TD in enumerate(self.parsed_data['Td'][-1]):
            Humidity_List.append(self.getHumidity(self.parsed_data['Temperature'][-1][index], TD))
        self.parsed_data['Humidity'].append(Humidity_List)

    @staticmethod
    def homogenise_data_sets(X, Y):
        X_out = np.ones((0, X.shape[1]), dtype=np.float64)
        Y_out = np.ones((0), dtype=np.float64)
        max_num_elements = np.sum(X[:, 2] == 6)
        for hour in set(X[:, 2]):
            num_elements = np.sum(X[:, 2] == hour)
            hour_where = np.where(X[:, 2] == hour)[0]
            if num_elements > max_num_elements:
                arr = np.arange(num_elements)
                np.random.shuffle(arr)
                hour_where = hour_where[arr[:max_num_elements]]
            X_out = np.vstack((X_out, X[hour_where, :]))
            Y_out = np.hstack((Y_out, Y[hour_where]))
        return X_out, Y_out

    def create_training_validation_set(self, X, Y, training_anteil=0.7):
        X_hom, Y_hom = self.homogenise_data_sets(X, Y)
        X_train, X_test, y_train, y_test = train_test_split(X_hom, Y_hom, test_size=training_anteil)
        return {'X_train': X_train,
                'y_train': y_train,
                'X_test': X_test,
                'y_test': y_test,
                'X_hom': X_hom,
                'Y_hom': Y_hom}

    def load_trainings_data(self, last_NR_data_to_ignore=0):
        MYSQL_config = {
            'mysql_host': self.configuration['MYSQL']['mysql_host'],
            'mysql_port': self.configuration.getint('MYSQL', 'mysql_port'),
            'mysql_username': self.configuration[self.name]['mysql_username'],
            'mysql_pw': self.configuration[self.name]['mysql_pw'],
            'mysql_DB': self.configuration[self.name]['mysql_DB'],
            'mysql_table': self.configuration[self.name]['mysql_tablename'],
            'time_zone': self.time_zone,
        }
        if 'mysql_type' in self.configuration[self.name].keys():
            MYSQL_config['StatementType'] = self.configuration[self.name]['mysql_type']
        MYsqlConnection = db_write(MYSQL_config)

        sql_str = "select \n" \
                  f" aggregate_pseudoData_for_prognosis.PowerWh AS DCPower, \n" \
                  f" Year({MYSQL_config['mysql_table']}.TIMESTAMP) as Jahr, \n" \
                  f" month({MYSQL_config['mysql_table']}.TIMESTAMP) as Monat, \n" \
                  f" hour({MYSQL_config['mysql_table']}.TIMESTAMP) as Stunde,  \n" \
                  f'{", ".join(self.value_list)} \n' \
                  f"FROM {MYSQL_config['mysql_table']} \n" \
                  "join aggregate_pseudoData_for_prognosis on " \
                  "TIMESTAMPADD(HOUR,1,aggregate_pseudoData_for_prognosis.TIMESTAMP) = " \
                  f"{MYSQL_config['mysql_table']}.TIMESTAMP \n"  # \
        # f"Where {MYSQL_config['mysql_table']}.Rad1h>1\n"

        with MYsqlConnection.connection.cursor() as cursor:
            # cursor.execute(("select * FROM %s;" % configuration[parser.name]['mysql_tablename']))
            cursor.execute(sql_str)
            records = cursor.fetchall()
            names = [x[0] for x in cursor.description]
        data_set_raw = np.array(records, dtype=np.float64)
        data_dict = {'columns': names,
                     'X_data_raw': data_set_raw[:, 1:],
                     'Y_data_raw': data_set_raw[:, 0],
                     'X_data': data_set_raw[:-last_NR_data_to_ignore - 1, 1:],
                     'Y_data': data_set_raw[:-last_NR_data_to_ignore - 1, 0]}

        data_dict.update(self.create_training_validation_set(data_dict['X_data'],
                                                             data_dict['Y_data'],
                                                             training_anteil=0.8))

        data_dict.update(
            {key: pd.DataFrame(value, columns=names[1:]) for key, value in data_dict.items() if key[0].upper() == 'X'})

        return data_dict

    def train_model(self, update_history=False, plotsize=0):
        new_model_found = False
        # get old_data
        input_data = self.load_trainings_data(last_NR_data_to_ignore=12*60*14)

        try:
            with open(self.AI_model_path, 'rb') as f:
                model = pickle.load(f)
            score_old = self.AI_model.score(input_data['X_data_raw'], input_data['Y_data_raw'])
        except Exception:
            model = self.AI_model
            score_old = -1

        model.fit(input_data['X_hom'], input_data['Y_hom'])

        score_new = model.score(input_data['X_data_raw'], input_data['Y_data_raw'])

        logger.info(f'\tscore(NEW): {score_new}')
        logger.info(f'\tscore(OLD): {score_old}')
        if score_new > score_old:  # (MAE_new < MAE_old and MAPE_new < MAPE_old*1.1) or
            with open(self.AI_model_path, 'wb') as f:
                pickle.dump(model, f)
            logger.info('Saving current model as it is better')
            self.AI_model = model
            if update_history:
                self.simulate_old_data()
            new_model_found = True
        else:
            logger.debug('Keeping old model')
            # return
        return new_model_found

    def explain_model(self):
        import shap
        import pandas as pd
        logging.getLogger('shap').setLevel(logging.WARNING)
        input_data = self.load_trainings_data(last_NR_data_to_ignore=12 * 60 * 14)
        if input_data['X_test'].shape[0]>1000:
            input_data['X_test'] = input_data['X_test'][:1000]
        shap.initjs()
        X_train_summary = shap.kmeans(input_data['X_hom'], 50)
        explainer = shap.KernelExplainer(self.AI_model.predict, X_train_summary)
        shap_values = explainer.shap_values(input_data['X_test'], nsamples=1000)
        shap.summary_plot(shap_values, input_data['X_test'], show=False)
        plt.tight_layout()
        plt.savefig(os.path.join(self.current_directory, 'Shap_Overview.png'))
        plt.close()
        for name in input_data['X_test'].columns.to_list():
            shap.dependence_plot(name, shap_values, input_data['X_test'], show=False)
            plt.tight_layout()
            plt.savefig(os.path.join(self.current_directory, f'Shap_Overview_{name}.png'))
            plt.close()

    def simulate_old_data(self):
        MYSQL_config = {
            'mysql_host': self.configuration['MYSQL']['mysql_host'],
            'mysql_port': self.configuration.getint('MYSQL', 'mysql_port'),
            'mysql_username': self.configuration[self.name]['mysql_username'],
            'mysql_pw': self.configuration[self.name]['mysql_pw'],
            'mysql_DB': self.configuration[self.name]['mysql_DB'],
            'mysql_table': self.configuration[self.name]['mysql_tablename'],
            'time_zone': self.time_zone,
        }
        if 'mysql_type' in self.configuration[self.name].keys():
            MYSQL_config['StatementType'] = self.configuration[self.name]['mysql_type']
        MYsqlConnection = db_write(MYSQL_config)

        # get old_data
        with MYsqlConnection.connection.cursor() as cursor:
            # cursor.execute(("select * FROM %s;" % configuration[parser.name]['mysql_tablename']))
            cursor.execute("select * FROM DWD_SIM_Daten;")
            record = cursor.fetchall()
            names = [x[0] for x in cursor.description]

        parsed_data = {}
        for index, key in enumerate(names):
            if key == 'TIMESTAMP':
                parsed_data[key] = [str(x[index]) for x in record]
            else:
                parsed_data[key] = [x[index] for x in record]

        logging_data = self.SIM_class.simulate_values(parsed_data)
        logging_data = self.AI_predict_values(logging_data)

        MYsqlConnection.write_dict_data(logging_data)


if __name__ == "__main__":
    from wakepy import set_keepawake, unset_keepawake
    from base_logging.base_logging import set_stream_logger
    import matplotlib.pyplot as plt

    set_stream_logger()
    logger.info('Test')
    logging.getLogger('base_MYSQL.mysql').setLevel(logging.WARNING)

    import configparser
    configuration = configparser.ConfigParser()
    configuration.sections()
    configuration.read(r'..\config.ini')
    set_keepawake(keep_screen_awake=True)

    try:
        parser_init = DWD_SIM_MLP(configuration)

        update_history_flag = False
        for i in range(1):
            logger.info(f'{i+1} th run:')
            if parser_init.train_model(update_history=True):
                update_history_flag = True
        if update_history_flag:
            parser_init.simulate_old_data()
            max_display = 7
            plt.figure(figsize=(1.5 * max_display + 1, 0.8 * max_display + 1))
            plt.plot(parser_init.AI_model.regressor_.steps[1][1].validation_scores_)
            plt.hlines(parser_init.AI_model.regressor_.steps[1][1].best_validation_score_, 0,
                       len(parser_init.AI_model.regressor_.steps[1][1].validation_scores_), colors='green')
            plt.vlines(
                len(parser_init.AI_model.regressor_.steps[1][1].validation_scores_) -
                parser_init.AI_model.regressor_.steps[1][1].n_iter_no_change - 2,
                0, 1, colors='green')
            plt.ylim([0.5, 1])
            plt.xlabel('Iteration')
            plt.ylabel('Score')
            plt.tight_layout()
            plt.savefig(os.path.join(parser_init.current_directory, 'ScoreCurve_Best_Fit.png'))
            plt.close()
            parser_init.explain_model()
    except Exception:
        logger.exception('Error at main')
    finally:
        unset_keepawake()
