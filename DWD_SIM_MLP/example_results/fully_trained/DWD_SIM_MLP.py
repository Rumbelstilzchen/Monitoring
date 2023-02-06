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
from sklearn.neural_network._multilayer_perceptron import _STOCHASTIC_SOLVERS
from sklearn.neural_network._base import LOSS_FUNCTIONS, DERIVATIVES
from sklearn.utils.extmath import safe_sparse_dot
from sklearn.compose import ColumnTransformer
from sklearn.compose import TransformedTargetRegressor
from sklearn.preprocessing import FunctionTransformer
from sklearn.preprocessing import MinMaxScaler

logger = logging.getLogger(__name__)


def check_values_empty(dict_data):
    for value in dict_data.values():
        if value == "":
            return True
    return False


name_configsection_SIM = 'DWD_SIM_SolarSystem'


def relative_abs_loss(y_true, y_pred):
    """Compute the squared loss for regression.

    Parameters
    ----------
    y_true : array-like or label indicator matrix
        Ground truth (correct) values.

    y_pred : array-like or label indicator matrix
        Predicted values, as returned by a regression estimator.

    Returns
    -------
    loss : float
        The degree to which the samples are correctly predicted.
    """
    return np.abs(1 - y_pred/y_true).mean()


LOSS_FUNCTIONS['relative'] = relative_abs_loss


class myMLPRegressor(MLPRegressor):
    def __init__(
        self,
        hidden_layer_sizes=(100,),
        activation="relu",
        *,
        solver="adam",
        alpha=0.0001,
        batch_size="auto",
        learning_rate="constant",
        learning_rate_init=0.001,
        power_t=0.5,
        max_iter=200,
        shuffle=True,
        random_state=None,
        tol=1e-4,
        verbose=False,
        warm_start=False,
        momentum=0.9,
        nesterovs_momentum=True,
        early_stopping=False,
        validation_fraction=0.1,
        beta_1=0.9,
        beta_2=0.999,
        epsilon=1e-8,
        n_iter_no_change=10,
        max_fun=15000,
    ):
        super().__init__(hidden_layer_sizes=hidden_layer_sizes,
                         activation=activation,
                         solver=solver,
                         alpha=alpha,
                         batch_size=batch_size,
                         learning_rate=learning_rate,
                         learning_rate_init=learning_rate_init,
                         power_t=power_t,
                         max_iter=max_iter,
                         shuffle=shuffle,
                         random_state=random_state,
                         tol=tol,
                         verbose=verbose,
                         warm_start=warm_start,
                         momentum=momentum,
                         nesterovs_momentum=nesterovs_momentum,
                         early_stopping=early_stopping,
                         validation_fraction=validation_fraction,
                         beta_1=beta_1,
                         beta_2=beta_2,
                         epsilon=epsilon,
                         n_iter_no_change=n_iter_no_change,
                         max_fun=max_fun,)
        self.out_activation_ = 'logistic'
        self.loss = 'relative'

    def _initialize(self, y, layer_units, dtype):
        # set all attributes, allocate weights etc. for first call
        # Initialize parameters
        self.n_iter_ = 0
        self.t_ = 0
        self.n_outputs_ = y.shape[1]

        # Compute the number of layers
        self.n_layers_ = len(layer_units)

        # Initialize coefficient and intercept layers
        self.coefs_ = []
        self.intercepts_ = []

        for ith in range(self.n_layers_ - 1):
            coef_init, intercept_init = self._init_coef(
                layer_units[ith], layer_units[ith + 1], dtype
            )
            self.coefs_.append(coef_init)
            self.intercepts_.append(intercept_init)

        if self.solver in _STOCHASTIC_SOLVERS:
            self.loss_curve_ = []
            self._no_improvement_count = 0
            if self.early_stopping:
                self.validation_scores_ = []
                self.best_validation_score_ = -np.inf
                self.best_loss_ = None
            else:
                self.best_loss_ = np.inf
                self.validation_scores_ = None
                self.best_validation_score_ = None

    def _backprop(self, X, y, activations, deltas, coef_grads, intercept_grads):
        """Compute the MLP loss function and its corresponding derivatives
        with respect to each parameter: weights and bias vectors.

        Parameters
        ----------
        X : {array-like, sparse matrix} of shape (n_samples, n_features)
            The input data.

        y : ndarray of shape (n_samples,)
            The target values.

        activations : list, length = n_layers - 1
             The ith element of the list holds the values of the ith layer.

        deltas : list, length = n_layers - 1
            The ith element of the list holds the difference between the
            activations of the i + 1 layer and the backpropagated error.
            More specifically, deltas are gradients of loss with respect to z
            in each layer, where z = wx + b is the value of a particular layer
            before passing through the activation function

        coef_grads : list, length = n_layers - 1
            The ith element contains the amount of change used to update the
            coefficient parameters of the ith layer in an iteration.

        intercept_grads : list, length = n_layers - 1
            The ith element contains the amount of change used to update the
            intercept parameters of the ith layer in an iteration.

        Returns
        -------
        loss : float
        coef_grads : list, length = n_layers - 1
        intercept_grads : list, length = n_layers - 1
        """
        n_samples = X.shape[0]

        # Forward propagate
        activations = self._forward_pass(activations)

        # Get loss
        loss_func_name = self.loss
        if loss_func_name == "log_loss" and self.out_activation_ == "logistic":
            loss_func_name = "binary_log_loss"
        loss = LOSS_FUNCTIONS[loss_func_name](y, activations[-1])
        # print(f'sqr {squared_loss(y,activations[-1])}\trel {loss}')
        # Add L2 regularization term to loss
        values = 0
        for s in self.coefs_:
            s = s.ravel()
            values += np.dot(s, s)
        loss += (0.5 * self.alpha) * values / n_samples

        # Backward propagate
        last = self.n_layers_ - 2

        # The calculation of delta[last] here works with following
        # combinations of output activation and loss function:
        # sigmoid and binary cross entropy, softmax and categorical cross
        # entropy, and identity with squared loss
        deltas[last] = activations[-1] - y

        # Compute gradient for the last layer
        self._compute_loss_grad(
            last, n_samples, activations, deltas, coef_grads, intercept_grads
        )

        inplace_derivative = DERIVATIVES[self.activation]
        # Iterate over the hidden layers
        for ind in range(self.n_layers_ - 2, 0, -1):
            deltas[ind - 1] = safe_sparse_dot(deltas[ind], self.coefs_[ind].T)
            inplace_derivative(activations[ind], deltas[ind - 1])

            self._compute_loss_grad(
                ind - 1, n_samples, activations, deltas, coef_grads, intercept_grads
            )

        return loss, coef_grads, intercept_grads


def lin_scaler(x, min_x=0, max_x=8500):
    return (x-min_x) / (max_x-min_x)


def lin_scaler_inverse(x, min_x=0, max_x=8500, output_check=False):
    x = x * (max_x-min_x) + min_x
    if np.any(x < 0) and output_check:
        logger.warning(f'values <0 found {np.sum(x < 0)*100/x.shape[0]:.1f}% of times: clipping to zero')
        x[np.where(x < 0)] = 0
    if np.any(x >= 10000) and output_check:
        logger.warning(f'values >=10000 found {np.sum(x >= 10000)*100/x.shape[0]:.1f}% of times: clipping to 9999.9')
        x[np.where(x >= 10000)] = 9999.9
    return x


def sin(X, period=360):
    return np.sin(X / period * 2 * np.pi)


def asin(X, period=360):
    return np.arcsin(X) * period / 2 / np.pi


def cos(X, period=360):
    return np.cos(X / period * 2 * np.pi)


def acos(X, period=360):
    return np.arccos(X) * period / 2 / np.pi


def output_log(x):
    return np.log1p(x)


def output_exp(x):
    x = np.exp(x) - 1
    if np.any(x < 0):
        logger.warning('values <0 found: clipping to zero')
        x[np.where(x < 0)] = 0
    if np.any(np.isnan(x)):
        logger.warning('NaN values found: clipping to zero')
    x[np.where(np.isnan(x))] = 0
    return x


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
        ("Jahr", FunctionTransformer(func=lin_scaler, kw_args={'min_x': 2019, 'max_x': 2048}), ['Jahr']),
        ("sin_month", FunctionTransformer(func=sin, kw_args={'period': 12}), ['Monat']),
        ("cos_month", FunctionTransformer(func=cos, kw_args={'period': 12}), ['Monat']),
        ("sin_hour", FunctionTransformer(func=sin, kw_args={'period': 24}), ['Stunde']),
        ("cos_hour", FunctionTransformer(func=cos, kw_args={'period': 24}), ['Stunde']),
        ("cos_Wind_direction", FunctionTransformer(func=cos, kw_args={'period': 360}), ["Wind_direction"]),
        ("sin_Wind_direction", FunctionTransformer(func=sin, kw_args={'period': 360}), ["Wind_direction"]),
        # ("Wind_direction", MinMaxScaler(feature_range=(-1, 1)), ["Wind_direction"]),
    ]

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

            regressor = myMLPRegressor(hidden_layer_sizes=(500, 250, 100, 50), max_iter=100000,
                                       warm_start=True,  # batch_size=10000,
                                       n_iter_no_change=250, early_stopping=True, validation_fraction=0.2)

            t_regressor = TransformedTargetRegressor(
                regressor,
                transformer=FunctionTransformer(func=lin_scaler, kw_args={'max_x': 8500},
                                                inverse_func=lin_scaler_inverse,
                                                inv_kw_args={'max_x': 8500, 'output_check': True}))
            # define transform
            transformer = ColumnTransformer(
                transformers=self.input_scaler,
                remainder=MinMaxScaler()
            )
            # define pipeline
            self.AI_model = Pipeline(steps=[('t', transformer), ('m', t_regressor)])
            # stacked_output_transformer = Pipeline(steps=[('1st', log_transformer), ('2nd', MinMaxScaler())])

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
        X_train, X_test, y_train, y_test = train_test_split(X_hom, Y_hom, train_size=training_anteil)
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
            # 'mysql_table': 'DWD_SIM_Daten',
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

    def train_model(self, update_history=False, last_NR_data_to_ignore=10*60*14):
        new_model_found = False
        # get old_data
        input_data = self.load_trainings_data(last_NR_data_to_ignore=last_NR_data_to_ignore)

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

    def explain_model(self, output_dir=None):
        import shap
        from shap.utils._legacy import DenseDataWithIndex
        if output_dir is None:
            output_dir = self.current_directory
        logging.getLogger('shap').setLevel(logging.WARNING)
        input_data = self.load_trainings_data(last_NR_data_to_ignore=0)
        if input_data['X_test'].shape[0] > 1000:
            input_data['X_test'] = input_data['X_test'][:1000]
        shap.initjs()
        X_train_summary = shap.kmeans(input_data['X_hom'], 50)
        X_train_summary = DenseDataWithIndex(X_train_summary.data, X_train_summary.group_names,
                                             list(range(X_train_summary.data.shape[0])), 'index', None,
                                             X_train_summary.weights)
        # X_train_summary = shap.sample(input_data['X_hom'], 100)
        explainer = shap.KernelExplainer(self.AI_model.predict, X_train_summary, keep_index=True)
        shap_values = explainer.shap_values(input_data['X_test'], nsamples=1000)
        shap.summary_plot(shap_values, input_data['X_test'], show=False)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'Shap_Overview.png'))
        plt.close()
        for name in input_data['X_test'].columns.to_list():
            shap.dependence_plot(name, shap_values, input_data['X_test'], show=False)
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, f'Shap_Overview_{name}.png'))
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
            # cursor.execute(f"select * FROM {configuration[self.name]['mysql_tablename']}")
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

    start_time = datetime.now(tz=pytz.timezone('Europe/Berlin'))

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

        outdir = os.path.join(parser_init.current_directory, 'Model_History', start_time.strftime('%Y-%m-%d_%H'))

        update_history_flag = False
        for i in range(100):
            logger.info(f'{i+1} th run:')
            if parser_init.train_model(update_history=True):
                os.makedirs(outdir, exist_ok=True)
                update_history_flag = True

                max_display = 7
                # plt.figure(figsize=(1.5 * max_display + 1, 0.8 * max_display + 1))
                fig, ax = plt.subplots(figsize=(1.5 * max_display + 1, 0.8 * max_display + 1))
                ax.plot(parser_init.AI_model.steps[1][1].regressor_.validation_scores_, label='Score (Validation)')
                ax.hlines(parser_init.AI_model.steps[1][1].regressor_.best_validation_score_, 0,
                          len(parser_init.AI_model.steps[1][1].regressor_.validation_scores_), colors='red')
                ax.vlines(len(parser_init.AI_model.steps[1][1].regressor_.validation_scores_) -
                          parser_init.AI_model.steps[1][1].regressor_.n_iter_no_change - 2,
                          0, 1, colors='red')
                ax.set_ylim(0.5, 1)
                ax.grid()
                ax.set_xlabel('Iteration')
                ax.set_ylabel('Score')
                ax2 = ax.twinx()
                ax2.plot(np.array(parser_init.AI_model.steps[1][1].regressor_.loss_curve_) * 100, color='green',
                         label='Loss (test)')
                ax2.set_ylabel('Loss')
                ax2.set_ylim(0, 100)
                # ax.legend(['Score (Validation)'])
                # ax2.legend(['Loss (test)'])
                fig.legend()
                fig.tight_layout()
                fig.savefig(os.path.join(outdir, 'ScoreCurve_Best_Fit.png'))
                plt.close()

                loss_score = np.array((parser_init.AI_model.steps[1][1].regressor_.loss_curve_,
                                       parser_init.AI_model.steps[1][1].regressor_.validation_scores_,
                                       np.arange(len(parser_init.AI_model.steps[1][1].regressor_.loss_curve_))),
                                      dtype=float).T
                best_loss = loss_score[np.where(
                    loss_score[:, 1] == parser_init.AI_model.steps[1][1].regressor_.best_validation_score_)][0]
                loss_score = loss_score[np.where(loss_score[:, 0] < 2)]
                loss_score2 = loss_score[np.where(loss_score[:, 0] < 1)]
                plt.figure(figsize=(1.5 * max_display + 1, 0.8 * max_display + 1))
                plt.subplot(121)
                plt.scatter(loss_score[:, 0] * 100, loss_score[:, 1], c=loss_score[:, 2], marker='.', s=0.5)
                plt.scatter(best_loss[0] * 100, best_loss[1], marker='x', c='red', s=10)
                plt.grid()
                cbar = plt.colorbar()
                cbar.set_label('Iteration', rotation=270)
                plt.xlabel('Train Loss')
                plt.ylabel('Val Score')
                plt.subplot(122)
                plt.scatter(loss_score2[:, 0] * 100, loss_score2[:, 1], c=loss_score2[:, 2], marker='.', s=0.5)
                plt.scatter(best_loss[0] * 100, best_loss[1], marker='x', c='red', s=10)
                plt.grid()
                cbar = plt.colorbar()
                cbar.set_label('Iteration', rotation=270)
                # plt.ylim(0.7, 1)
                plt.xlabel('Train Loss')
                plt.ylabel('Val Score')
                plt.savefig(os.path.join(outdir, 'Score_LossCurve_Best_Fit.png'))
                plt.close()

        if update_history_flag:
            from shutil import copyfile
            copyfile(os.path.join(parser_init.current_directory, 'MLP_model.bin'),
                     os.path.join(outdir, 'MLP_model.bin'))
            copyfile(os.path.join(parser_init.current_directory, 'DWD_SIM_MLP.py'),
                     os.path.join(outdir, 'DWD_SIM_MLP.py'))
            parser_init.explain_model(outdir)
    except Exception:
        logger.exception('Error at main')
    finally:
        unset_keepawake()
