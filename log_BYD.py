# -*- coding: utf-8 -*-

import logging
from base_logging.base_logging import set_logger
from base_MYSQL.mysql import db_write
from BYD.BYD import BYD as parser
from base_monitoring.monitoring import Monitoring
import configparser


if __name__ == "__main__":
    set_logger('logfile_%s.log' % parser.name)
    logger = logging.getLogger(__name__)
    logger.info('First Log')
    configuration = configparser.ConfigParser()
    configuration.sections()
    configuration.read('config.ini')

    refreshrate = configuration.getint(parser.name, 'refreshrate')
    writerate = configuration.getint(parser.name, 'writerate')

    if parser.name in configuration.sections():
        try:
            parser_init = parser(configuration)
        except Exception as e:
            logging.exception('on load %s class', parser.name)
            raise e

    try:
        MYSQL_config = {
            'mysql_host': configuration['MYSQL']['mysql_host'],
            'mysql_port': configuration.getint('MYSQL', 'mysql_port'),
            'mysql_username': configuration[parser.name]['mysql_username'],
            'mysql_pw': configuration[parser.name]['mysql_pw'],
            'mysql_DB': configuration[parser.name]['mysql_DB'],
            'mysql_table': configuration[parser.name]['mysql_tablename'],
            'time_zone': parser_init.time_zone,
        }
        MYsqlConnection = db_write(MYSQL_config)
    except Exception as e:
        logger.exception('on load MYSQL class')
        raise e

    if 'Mail' in configuration.sections():
        mail_config = configuration['Mail']
    else:
        mail_config = None

    Monitoring = Monitoring(refreshrate, writerate, parser_init, MYsqlConnection, mail_config)

    Monitoring.start()
