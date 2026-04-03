# -*- coding: utf-8 -*-

import logging
from base_classes.db_wrapper import influxdb2, mysql

logger = logging.getLogger(__name__)


class db_write:
    connection = None

    def __init__(self, config):
        self.config = config
        self.db_connections = {}
        if 'influxdb2' in self.config.keys():
            self.db_connections['influxdb2'] = (influxdb2.db_write(self.config['influxdb2']))
        if 'mysql' in self.config.keys():
            self.db_connections["mysql"] = (mysql.db_write(self.config['mysql']))
        #self.connect(info_output=True)

    def __del__(self):
        self.close()

    def connect(self, info_output=False):
        try:
            for db_connection in self.db_connections.values():
                db_connection.connect(info_output=info_output)
        except Exception as e:
            logger.exception('Mysql cannot connect')
            raise e

    def close(self):
        try:
            for db_connection in self.db_connections.values():
                db_connection.close()
        except Exception:
            logger.exception('Mysql already closed')

    def check_connection(self):
        return all(db_connection.check_connection() for db_connection in self.db_connections.values() if db_connection is not None)

    def write_dict_data(self, myDict: dict):
        return all(db_connection.write_dict_data(myDict) for db_connection in self.db_connections.values() if db_connection is not None)
