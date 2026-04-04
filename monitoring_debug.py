# -*- coding: utf-8 -*-

import logging

from base_classes.config import ConfigDict, get_config_value, load_config
from base_classes.db_wrapper import db_write
from base_classes.base_logging import set_logger
from base_classes.monitoring import Monitoring as Monitoring_class

# from USV_modbus.USV_modbus import USV_modbus as parser
# from Kostal.Kostal import Kostal as parser
#from Kostal_Piko_BA.Kostal_Piko_BA import Kostal_Piko_BA as parser

# Import monitoring module by cmdline argument
# if len(sys.argv) <= 1:
#     raise RuntimeError("Too less arguments calling script")
# else:
#     module_name = sys.argv[1]
# parser = getattr(importlib.import_module("%s.%s" % (module_name, module_name)), module_name)
# parser = getattr(__import__("%s.%s" % (module_name,module_name), fromlist=[module_name]), module_name)

# For debugging purposes any of the lines below does the same thing but static
# from devices_to_monitor.Kostal_Piko_BA import Kostal_Piko_BA as parser
# from devices_to_monitor.Elgris import Elgris as parser
# from devices_to_monitor.GoE_Garage import GoE_Garage as parser
# from devices_to_monitor.BYD import BYD as parser
# from devices_to_monitor.BYD_Cell_voltage import BYD_Cell_voltage as parser
# from devices_to_monitor.DWD_SIM import DWD_SIM as parser
# from devices_to_monitor.USV import USV as parser
from devices_to_monitor.Luxtronik import Luxtronik as parser


def main():
    set_logger("logfile_%s.log" % parser.name)
    logger = logging.getLogger(__name__)
    logger.info("First Log")

    # Load YAML configuration
    configuration = load_config()

    refreshrate = get_config_value(
        configuration, parser.name, "refreshrate_debug", default=10
    )
    writerate = get_config_value(
        configuration, parser.name, "writerate_debug", default=60
    )

    if parser.name in configuration:
        try:
            # Create a dict-like object compatible with configparser for backward compatibility
            config_wrapper = ConfigDict(configuration)
            parser_init = parser(config_wrapper)
        except Exception as e:
            logging.exception("on load %s class", parser.name)
            raise e
    else:
        logger.error(
            "section %s for monitoring module not found in config.yaml", parser.name
        )
        raise RuntimeError(
            "section %s for monitoring module not found in config.yaml" % parser.name
        )

    try:
        DB_config = {db_type: settings for db_type, settings in configuration['DB_global'].items() if db_type in configuration[parser.name]}
        for db_type in DB_config:
            DB_config[db_type].update(configuration[parser.name][db_type])

        if 'influxdb2' in DB_config:
            DB_config['influxdb2']['tags'] = parser_init.influx_tags

        DBConnection = db_write(DB_config)
    except Exception as e:
        logger.exception("on load MYSQL class")
        DBConnection = None
        # raise e

    mail_config = get_config_value(configuration, "Mail")

    Monitoring = Monitoring_class(
        refreshrate, writerate, parser_init, DBConnection, mail_config
    )
    Monitoring.start()


if __name__ == "__main__":
    main()
