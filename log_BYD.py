# -*- coding: utf-8 -*-

import logging
from base_MYSQL.mysql import db_write
from base_monitoring.monitoring import Monitoring
from BYD.BYD import BYD
import configparser
logging.basicConfig(filename='logfile_BYD.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)-8s : %(message)s', datefmt='%Y%m%d-%H%M%S')

monitor_name = 'BYD'

if __name__ == "__main__":
    configuration = configparser.ConfigParser()
    configuration.sections()
    configuration.read('config.ini')

    refreshrate = configuration.getint(monitor_name, 'refreshrate')
    writerate = configuration.getint(monitor_name, 'writerate')

    if monitor_name in configuration.sections():
        try:
            BYD = BYD(configuration)
        except Exception as e:
            logging.exception('on load BYD class')
            raise e

    try:
        MYSQL_config = {
            'mysql_host': configuration['MYSQL']['mysql_host'],
            'mysql_port': configuration.getint('MYSQL', 'mysql_port'),
            'mysql_username': configuration[monitor_name]['mysql_username'],
            'mysql_pw': configuration[monitor_name]['mysql_pw'],
            'mysql_DB': configuration[monitor_name]['mysql_DB'],
            'mysql_table': configuration[monitor_name]['mysql_tablename']
        }
        MYsqlConnection = db_write(MYSQL_config)
    except Exception as e:
        logging.exception('on load MYSQL class')
        raise e

    Monitoring = Monitoring(refreshrate, writerate, BYD, MYsqlConnection)

    Monitoring.start()