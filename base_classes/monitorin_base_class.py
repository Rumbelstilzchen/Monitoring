import logging

logger = logging.getLogger(__name__)


class Base_Parser:
    def __init__(self):
        self.parsed_data = {}
        self.average_ignores = []
        self.suppress_zeros = []
        self.nr_of_decimal_for_round = {"default": 6}
        self.accumulated_data = {}

    def collect_data(self):
        logger.error("method must be implemented in child class")
        raise NotImplementedError

    def set_averages(self, logging_data):
        pass

    def exit_parser(self):
        logger.warning("nothing done - method should be implemented in child class")
