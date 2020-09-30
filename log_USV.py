# -*- coding: utf-8 -*-

import logging
from base_logging.base_logging import set_logger
from base_MYSQL.mysql import db_write
from base_monitoring.monitoring import Monitoring
from USV.USV import USV
import configparser


if __name__ == "__main__":
#     logging.basicConfig(level='DEBUG', format='%(asctime)s %(levelname)-8s : %(message)s', datefmt='%Y%m%d-%H%M%S')
# #    logging.basicConfig(filename='logfile_USV.log', level='DEBUG', format='%(asctime)s %(levelname)-8s : %(message)s', datefmt='%Y%m%d-%H%M%S')
#     logger = logging.getLogger(__name__)
    set_logger('logfile_USV.log')
    logger = logging.getLogger(__name__)
    logger.info('First Log')
    monitor_name = 'USV'
    configuration = configparser.ConfigParser()
    configuration.sections()
    configuration.read('config.ini')

    refreshrate = configuration.getint(monitor_name, 'refreshrate')
    writerate = configuration.getint(monitor_name, 'writerate')

    if monitor_name in configuration.sections():
        try:
            USV = USV(configuration)
        except Exception as e:
            logger.exception('on load %s class', monitor_name)
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
        logger.exception('on load MYSQL class')
        raise e

    Monitoring = Monitoring(refreshrate, writerate, USV, MYsqlConnection)

    Monitoring.start()
