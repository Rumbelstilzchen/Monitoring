# -*- coding: utf-8 -*-

import logging
# import pymysql as mysql
import mysql.connector as mysql
from collections import OrderedDict
logger = logging.getLogger(__name__)
# logger = logging.getLogger()


class db_write:
    connection = None

    def __init__(self, config):
        self.config = config
        if 'StatementType' in self.config.keys():
            self.statement_type = self.config['StatementType']
        else:
            self.statement_type = 'Insert'
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
                                            charset='utf8')
            if 'time_zone' in self.config.keys():
                self.connection.time_zone = self.config['time_zone']
            else:
                self.connection.time_zone = 'Europe/Berlin'

            if self.connection.is_connected():
                db_Info = self.connection.get_server_info()
                logger.info("Connected to MySQL Server version %s", db_Info)
                with self.connection.cursor() as cursor:
                    cursor.execute("select database();")
                    record = cursor.fetchone()
                    logger.info("You're connected to database: %s", record)
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
        if isinstance(myDict['TIMESTAMP'], list):
            success_state = self.write_dict_data_multiple(myDict)
        else:
            success_state = self.write_dict_data_single(myDict)
        return success_state

    def write_dict_data_multiple(self, myDict):
        success = True
        if 'time_sec' in myDict.keys():
            time_column = 'time_sec'
        elif 'TIMESTAMP' in myDict.keys():
            time_column = 'TIMESTAMP'
        else:
            logger.error('Cannot Update Entries - deleteing is not possible as neither time_sec nor TIMESTAMP is found')
            raise NotImplementedError
        if self.statement_type.upper() == 'UPDATE':
            try:
                with self.connection.cursor() as cursor:
                    sql_delete = 'DELETE FROM %s WHERE %s >= %s' % (self.config['mysql_table'], time_column, myDict[time_column][0])
                    cursor.execute(sql_delete)
                    self.connection.commit()
                logger.debug("MYSQL: deleting old entries")
                success = True
            except Exception:
                success = False
                logger.exception('MYSQLERROR')
        try:
            placeholders = ', '.join(['%s'] * len(myDict))
            columns = ', '.join(myDict.keys())
            sql = "INSERT INTO %s ( %s ) VALUES ( %s )" % (self.config['mysql_table'], columns, placeholders)
            entry_list = []
            for index in range(len(myDict[time_column])):
                entry_list.append(tuple([x[index] for x in myDict.values()]))
            with self.connection.cursor() as cursor:
                cursor.executemany(sql, entry_list)
                # for index in range(len(myDict[time_column])):
                #     cursor.execute(sql, [x[index] for x in myDict.values()])
                self.connection.commit()
                # logger.debug("MYSQL: %s", str([x[index] for x in myDict.values()]))
                logger.debug("MYSQL: first element: %s", str(entry_list[0]))
        except Exception:
            logger.exception('MYSQLERROR')
            success = False
        return success

    def write_dict_data_single(self, myDict):
        # if self.statement_type.upper() == 'UPDATE':
        #     # delete old entries
        #     pass
        try:
            with self.connection.cursor() as cursor:
                placeholders = ', '.join(['%s'] * len(myDict))
                columns = ', '.join(myDict.keys())
                sql = "INSERT INTO %s ( %s ) VALUES ( %s )" % (self.config['mysql_table'], columns, placeholders)
                cursor.execute(sql, [x for x in myDict.values()])
                self.connection.commit()
            logger.debug("MYSQL: %s", str([x for x in myDict.values()]))
            success = True
        except Exception:
            logger.exception('MYSQLERROR')
            success = False
        return success
