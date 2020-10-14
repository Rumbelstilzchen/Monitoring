# -*- coding: utf-8 -*-

import logging
from base_logging.base_logging import set_logger
from base_MYSQL.mysql import db_write
from Kostal.Kostal import Kostal
from base_monitoring.monitoring import Monitoring
import configparser

monitor_name = 'Kostal'

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
            Kostal = Kostal(configuration)
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
            'mysql_table': configuration[monitor_name]['mysql_tablename'],
            'time_zone': Kostal.time_zone,
        }
        MYsqlConnection = db_write(MYSQL_config)
    except Exception as e:
        logger.exception('on load MYSQL class')
        raise e

    if 'Mail' in configuration.sections():
        mail_config = configuration['Mail']

    Monitoring = Monitoring(refreshrate, writerate, Kostal, MYsqlConnection, mail_config)

    Monitoring.start()
