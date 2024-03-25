# -*- coding: utf-8 -*-

import logging
from logging.handlers import RotatingFileHandler


def set_stream_logger():
    logging.root.setLevel(logging.INFO)
    # create formatter and add it to the handler
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')

    for hdlr in logging.root.handlers:
        logging.root.handlers.remove(hdlr)

    # create console handler with a higher log level
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    # add the handler to the logger
    logging.root.addHandler(handler)

    logger = logging.getLogger(__name__)
    logger.info('Logging initialized')


def set_logger(filename):
    logging.root.setLevel(logging.INFO)
    # create formatter and add it to the handler
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')

    for hdlr in logging.root.handlers:
        logging.root.handlers.remove(hdlr)

    # # create console handler with a higher log level
    # handler = logging.StreamHandler()
    # handler.setLevel(logging.DEBUG)
    # handler.setFormatter(formatter)
    # # add the handler to the logger
    # logging.root.addHandler(handler)

    handler_file = RotatingFileHandler(filename, maxBytes=1024*2024, backupCount=0, encoding="utf-8", )
    handler_file.setFormatter(formatter)
    handler_file.setLevel(logging.INFO)
    logging.root.addHandler(handler_file)

    logger = logging.getLogger(__name__)
    logger.info('Logging initialized')
