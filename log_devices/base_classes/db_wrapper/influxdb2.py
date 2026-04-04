# -*- coding: utf-8 -*-

import logging

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS, WriteOptions, WriteType

logger = logging.getLogger(__name__)

# BATCHING = WriteOptions(write_type=WriteType.batching, batch_size=1000, flush_interval=10000, jitter_interval=2000, retry_interval=5000, max_retries=5, max_retry_delay=30000, exponential_base=2)
BATCHING = WriteOptions(
    write_type=WriteType.batching,
    batch_size=5000,
    flush_interval=5000,
    jitter_interval=1000,
    retry_interval=5000,
    max_retries=5,
    max_retry_delay=30000,
    exponential_base=2,
)


def dict_to_point(dictionary, field_name, field_value, time_sec):
    point = Point(dictionary["measurement"])
    for tag_key, tag_value in dictionary["tags"].items():
        point.tag(tag_key, tag_value)
    point.field(field_name, field_value)
    point.time(time_sec, WritePrecision.S)
    return point


class db_write:
    connection = None
    write_api = None

    def __init__(self, config):
        self.config = config
        if "StatementType" in self.config.keys():
            self.statement_type = self.config["StatementType"]
        else:
            self.statement_type = "Insert"
        self.influx_tags = config['tags']
        self.connect(info_output=True)

    def __del__(self):
        self.close()

    def connect(self, info_output=False):
        try:
            self.connection = InfluxDBClient(
                url=f"http://{self.config['host']}:{self.config['port']}",
                token=self.config["token"],
                org=self.config["org"],
            )

            if self.connection.ping():
                db_Info = self.connection.build()
                db_version = self.connection.version()
                if info_output:
                    logger.info(
                        "Connected to INfluxDB2 Server version %s %s",
                        db_Info,
                        db_version,
                    )
        except Exception as e:
            logger.exception("Influx cannot connect")
            raise e

    def close(self):
        try:
            self.connection.close()
        except Exception:
            logger.exception("Influx already closed")

    def check_connection(self):
        must_connect = False
        return_status = False
        try:
            return_status = self.connection.ping()
        except Exception:
            must_connect = True
            logger.exception(
                "Not Connected to Influx reconnect didn't work - trying to reconnect"
            )
        if must_connect:  # reconnect your cursor as you did in __init__ or wherever
            try:
                self.connect()
                return_status = True
            except Exception:
                return_status = False
        return return_status

    def write_dict_data(self, logging_data: dict, batch=False):

        data = [
            dict_to_point(
                dict,
                field_name,
                val_type(logging_data[key]),
                logging_data["time_sec"],
            )
            for key, (
                field_name,
                val_type,
                dict,
            ) in self.influx_tags.items()
            if key in logging_data and logging_data[key] is not None
        ]

        if not self.check_connection():
            return False
        write_options = SYNCHRONOUS
        if batch:
            write_options = BATCHING
        with self.connection.write_api(write_options=write_options) as write_api:
            try:
                write_api.write(
                    bucket=self.config["bucket"], record=data
                )  # , write_precision=WritePrecision.S )
            except Exception:
                logger.exception("Influx Write Error")
                return False
        return True
