# -*- coding: utf-8 -*-

import os
import logging
from datetime import datetime
import time
from collections import OrderedDict
logger = logging.getLogger(__name__)


class Monitoring:
    
    def __init__(self, refreshrate, writerate, data_parser=None, mysql_connection=None, mail_config=None):
        self.refreshrate = refreshrate
        self.writerate = writerate
        self.samples_per_write = int(writerate/refreshrate)
        self.refreshrate = self.writerate/self.samples_per_write
        self.mysql_connection = mysql_connection
        self.data_parser = data_parser
        self.mail_settings = mail_config
        
    def start(self):
        max_number_cached_entries = 6
        counter = 0
        logger.debug(counter)
        # logger.info(datetime.now().isoformat())
        waiting = (self.writerate - (datetime.now().timestamp() % self.writerate)) + self.refreshrate - 2
        if waiting > self.writerate:
            waiting = waiting - self.writerate
    
        # logger.info('Waittime: ' + str(waiting))
        time.sleep(waiting)
        mysql_status_counter = 0
        data_caching = False
        data_cache = []
        unsuccessful_counter = 0
        try:
            while True:
                logging_list = []
                for i in range(self.samples_per_write):
                    if i == 0:
                        waiting = (self.writerate - (datetime.now().timestamp() % self.writerate)) + self.refreshrate - 1
                        if waiting > self.writerate:
                            waiting = waiting - self.writerate
                        time.sleep(waiting)
                    time.sleep(self.refreshrate - (datetime.now().timestamp() % self.refreshrate))

                    if self.data_parser is not None:
                        try:
                            logging_list.append(self.data_parser.collect_data())
                        except Exception:
                            logger.exception('No Data from parser')
                        logger.debug('\t parsed_data: %s' % self.data_parser.parsed_data['TIMESTAMP'])

                if len(logging_list) > 0:
                    unsuccessful_counter = 0
                    if len(logging_list) > 1:
                        logging_data = self.average_of_dicts(logging_list, self.data_parser.average_ignores, 6)
                    else:
                        logging_data = logging_list[0]
                    if not data_caching:
                        if self.writerate >= 300:
                            try:
                                self.mysql_connection.connect()
                            except Exception:
                                mysql_status = False
                            else:
                                mysql_status = self.mysql_connection.write_dict_data(logging_data)
                        else:
                            mysql_status = self.mysql_connection.write_dict_data(logging_data)
                        if not mysql_status:
                            data_caching = True
                            data_cache = [logging_data]
                            mysql_status_counter += 1
                            logger.info("\tcaching enabled")
                            logger.info("\t\t writing to cache")
                            self.mysql_connection.close()
                        elif self.writerate >= 300:
                            self.mysql_connection.close()
                        # else:
                        #     logger.info('\tMYSQL: %s' % logging_data['TIMESTAMP'])
                    elif mysql_status_counter == max_number_cached_entries:
                        data_cache.append(logging_data)
                        logger.info("\t\t writing to cache")
                        mysql_status_list = []
                        self.mysql_connection.connect(info_output=True)
                        for logging_data in data_cache:
                            mysql_status = self.mysql_connection.write_dict_data(logging_data)
                            if not mysql_status:
                                logger.warning('\t\tMYSQL: %s' % logging_data['TIMESTAMP'])
                            mysql_status_list.append(mysql_status)
                        if self.writerate >= 300:
                            self.mysql_connection.close()
                        if all(mysql_status_list):
                            logger.info("\tcaching disabled - Data Cache written to mysql")
                            data_caching = False
                            mysql_status_counter = 0
                        elif not any(mysql_status_list):
                            logger.error("Data Cache not written to mysql")
                            raise RuntimeError
                        else:
                            logger.warning("Data Cache partially written to mysql")
                            raise RuntimeError
                    else:
                        data_cache.append(logging_data)
                        mysql_status_counter += 1
                        logger.info("\t\t writing to cache")
                else:
                    logger.error('No data was received from parser and written to DB')
                    unsuccessful_counter += 1
                    if unsuccessful_counter == 5:
                        raise IOError('To many unsuccessful tries')
        except Exception as e:
            logger.exception('Aborting now')
            if self.mail_settings is not None:
                successfully_attached_file = self.send_mail()
                if successfully_attached_file is not None:
                    os.remove(successfully_attached_file)
            raise e

    def send_mail(self):
        import smtplib
        import ssl
        from email import encoders
        from email.mime.base import MIMEBase
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        filename = None
        for handler in logging.root.handlers:
            if hasattr(handler, 'baseFilename'):
                filename = handler.baseFilename
                logging.root.handlers.remove(handler)
        if filename is None:
            return None
        # Create a secure SSL context
        ssl_context = ssl.create_default_context()

        body = "This is an email with attachment sent from Python"

        # Create a multipart message and set headers
        message = MIMEMultipart()
        message["From"] = self.mail_settings['From']
        message["To"] = self.mail_settings['To']
        message["Subject"] = 'Error on Logging - Logfile attached'

        # Add body to email
        message.attach(MIMEText(body, "plain"))

        # Open log-file in binary mode
        with open(filename, "rb") as attachment:
            # Add file as application/octet-stream
            # Email client can usually download this automatically as attachment
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
        # Encode file in ASCII characters to send by email
        encoders.encode_base64(part)
        # Add header as key/value pair to attachment part
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {os.path.basename(filename)}",
        )
        # Add attachment to message and convert message to string
        message.attach(part)

        with smtplib.SMTP_SSL(self.mail_settings['Server'], self.mail_settings['port'], context=ssl_context) as server:
            server.login(self.mail_settings['From'], self.mail_settings['Password'])
            # errors = server.sendmail(self.mail_settings['From'], self.mail_settings['To'], message.as_string())
            errors = server.send_message(message)
        if len(errors) == 0:
            return filename
        else:
            for key, value in errors.items():
                print("%s: %s" %(key, value))
            return None

    @staticmethod
    def average_of_dicts(input_dict, list_of_ignores, decimals):
        # print(str(input_dict))
        output = OrderedDict()
        length = float(len(input_dict))
        for k in input_dict[0].keys():
            if k in list_of_ignores:
                output[k] = input_dict[-1][k]
            else:
                output[k] = round(sum(t[k] for t in input_dict) / length, decimals)
        return output
