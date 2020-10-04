# -*- coding: utf-8 -*-

import logging
from base_logging.base_logging import set_logger
from base_MYSQL.mysql import db_write
from DWD.DWD import DWD
from base_monitoring.monitoring import Monitoring
import configparser
# logging.basicConfig(filename='logfile_kostal.log', level=logging.INFO,
#                     format='%(asctime)s %(levelname)-8s : %(message)s', datefmt='%Y%m%d-%H%M%S')

monitor_name = 'DWD'

if __name__ == "__main__":
    set_logger('logfile_%s.log' % monitor_name)
    logger = logging.getLogger(__name__)
    logger.info('First Log')
    configuration = configparser.ConfigParser()
    configuration.sections()
    configuration.read('config.ini')

    refreshrate = configuration.getint(monitor_name, 'refreshrate')
    writerate = configuration.getint(monitor_name, 'writerate')

    if monitor_name in configuration.sections():
        try:
            DWD = DWD(configuration)
        except Exception as e:
            logging.exception('on load Kostal class')
            raise e

    try:
        MYSQL_config = {
            'mysql_host': configuration['MYSQL']['mysql_host'],
            'mysql_port': configuration.getint('MYSQL', 'mysql_port'),
            'mysql_username': configuration[monitor_name]['mysql_username'],
            'mysql_pw': configuration[monitor_name]['mysql_pw'],
            'mysql_DB': configuration[monitor_name]['mysql_DB'],
            'mysql_table': configuration[monitor_name]['mysql_tablename'],
            'StatementType': 'UPDATE'
        }
        MYsqlConnection = db_write(MYSQL_config)
    except Exception as e:
        logging.exception('on load MYSQL class')
        raise e

    Monitoring = Monitoring(refreshrate, writerate, DWD, MYsqlConnection)

    Monitoring.start()
