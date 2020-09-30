# -*- coding: utf-8 -*-

import logging
import pymysql as mysql
from collections import OrderedDict
logger = logging.getLogger(__name__)
# logger = logging.getLogger()


class db_write:
    connection = None

    def __init__(self, config):
        self.config = config
        self.connect()

    def __del__(self):
        self.close()

    def connect(self):
        try:
            self.connection = mysql.connect(host=self.config['mysql_host'],
                                            port=self.config['mysql_port'],
                                            user=self.config['mysql_username'],
                                            password=self.config['mysql_pw'],
                                            db=self.config['mysql_DB'],
                                            charset='utf8mb4')
        except Exception as e:
            logger.exception('Mysql cannot connect')
            raise e

    def close(self):
        try:
            self.connection.close()
        except Exception:
            logger.exception('Mysql already closed')

    def write_dict_data(self, dictionary):
        myDict = OrderedDict(dictionary)
        try:
            # with self.connection.cursor() as cursor:
            #     placeholders = ', '.join(['%s'] * len(myDict))
            #     columns = ', '.join(myDict.keys())
            #     sql = "INSERT INTO %s ( %s ) VALUES ( %s )" % (self.config['mysql_table'], columns, placeholders)
            #     cursor.execute(sql, [x for x in myDict.values()])
            #     result = self.connection.commit()
            #     if result is not None:
            #         logger.warning('MYSQL_return: %s' % str(result))
            logger.info("MYSQL: %s", str([x for x in myDict.values()]))
            success = True
        except Exception:
            logger.exception('MYSQLERROR')
            success = False
        return success
