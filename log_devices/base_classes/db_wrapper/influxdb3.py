# -*- coding: utf-8 -*-

import logging

# import pymysql as mysql
from influxdb_client_3 import (
    InfluxDBClient3,
    InfluxDBError,
    WriteOptions,
    WritePrecision,
    WriteType,
    write_client_options,
)

logger = logging.getLogger(__name__)


# logger = logging.getLogger()
def success(self, data: str):
    return
    print(f"Successfully wrote batch: data: {data}")


def error(self, data: str, exception: InfluxDBError):
    print(f"Failed writing batch: config: {self}, data: {data} due: {exception}")
    raise RuntimeError(f"Failed writing batch: config: {self}, data: {data}")


def retry(self, data: str, exception: InfluxDBError):
    print(
        f"Failed retry writing batch: config: {self}, data: {data} retry: {exception}"
    )


class db_write:
    connection = None
    write_api = None

    def __init__(self, config):
        self.config = config
        self.connect(info_output=True)

    def __del__(self):
        self.close()

    def connect(self, info_output=False):
        try:
            # Configure options for batch writing.
            write_options = WriteOptions(
                write_type=WriteType.batch,
                batch_size=500,
                flush_interval=10_000,
                jitter_interval=2_000,
                retry_interval=5_000,
                max_retries=5,
                max_retry_delay=30_000,
                exponential_base=2,
            )

            # Create an options dict that sets callbacks and WriteOptions.
            wco = write_client_options(
                success_callback=success,
                error_callback=error,
                retry_callback=retry,
                write_options=write_options,
            )

            wco_single = write_client_options(
                write_options=WriteType.synchronous,
                success_callback=success,
                error_callback=error,
                retry_callback=retry,
            )
            self.connection = InfluxDBClient3(
                host=f"http://{self.config['influx_host']}:{self.config['influx_port']}",
                token=self.config["influx_token"],
                database=self.config["influx_bucket"],
                write_client_options=wco,
            )
            self.connection_single = InfluxDBClient3(
                host=f"http://{self.config['influx_host']}:{self.config['influx_port']}",
                token=self.config["influx_token"],
                database=self.config["influx_bucket"],
                write_client_options=wco_single,
            )
        except Exception as e:
            logger.exception("Mysql cannot connect")
            raise e

    def close(self):
        try:
            self.connection.close()
        except Exception:
            logger.exception("Mysql already closed")

    def check_connection(self):
        return True

    def write_dict_data(self, myDict):
        success_state = True
        if self.check_connection():
            try:
                self.connection.write(myDict, write_precision=WritePrecision.S)
            except Exception:
                logger.exception("Influx Write Error")
                success_state = False
        else:
            success_state = False
        return success_state

    def write_dict_data_single(self, myDict):
        success_state = True
        if self.check_connection():
            try:
                for data in myDict:
                    self.connection_single.write(data, write_precision=WritePrecision.S)
            except Exception:
                logger.exception("Influx Write Error")
                print(f"Failed writing data:\n{data}")
                success_state = False
        else:
            success_state = False
        return success_state
