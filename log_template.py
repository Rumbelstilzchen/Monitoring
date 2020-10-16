# -*- coding: utf-8 -*-

import logging
from base_logging.base_logging import set_logger
from base_MYSQL.mysql import db_write
from base_monitoring.monitoring import Monitoring
import configparser
import sys
import importlib

# Import monitoring module by cmdline argument
if len(sys.argv) <= 1:
    exit("Too less arguments calling script")
else:
    module_name = sys.argv[1]
parser = getattr(importlib.import_module("%s.%s" % (module_name, module_name)), module_name)
# parser = getattr(__import__("%s.%s" % (module_name,module_name), fromlist=[module_name]), module_name)

# For debugging purposes this line below does the same thing but static
# from BYD.BYD import BYD as parser
# from Kostal.Kostal import Kostal as parser
# from DWD.DWD import DWD as parser
# from USV.USV import USV as parser


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
        if 'mysql_type' in configuration[parser.name].keys():
            MYSQL_config['StatementType'] = configuration[parser.name]['mysql_type']
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
