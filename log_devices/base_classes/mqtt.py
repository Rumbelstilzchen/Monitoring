# -*- coding: utf-8 -*-
import os
import json
import logging
import paho.mqtt.client as mqtt
from retry import retry

logger = logging.getLogger(__name__)


class MQTTBase:
    def __init__(self, name, configuration,suppress_zeros=None,topics=None, receiver_method=None):
        self.name = name
        self.config = configuration
        self.suppress_zeros = [] if suppress_zeros is None else suppress_zeros
        self.mqtt_client = None
        self.mqtt_topic = ""
        self.mqtt_data = {}
        self.receiver_method = receiver_method
        self.topics = topics
        self.connect_mqtt()

    def _on_connect(self, client, userdata, flags, reason_code, properties):
        logger.info(f"Connecting - setting online status - rc: {reason_code}")
        client.publish(
            f"equipment/{self.name}/connection",
            "online",
            qos=1,
            retain=True,
        )
        if self.topics is not None:
            for topic in self.topics:
                client.subscribe(topic, 0)
                logger.info(f"Subscribed to {topic}")

    def _on_disconnect(self, client, userdata, flags, rc,properties):
        if rc != 0:
            logger.warning(f"Unexpected disconnection: {rc}")
            # Automatischer Reconnect durch paho-mqtt

    @retry(tries=4, delay=10, backoff=1.5, logger=logger)
    def connect_mqtt(self):
        if self.config is None:
            return

        logger.info("Connecting to MQTT")
        self.mqtt_topic = self.config["topic"]
        self.mqtt_client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id=f"{self.name}_monitoring",
            clean_session=False,
            protocol=mqtt.MQTTv311,
        )  # create new instance
        self.mqtt_client.will_set(
            f"equipment/{self.name}/connection", "offline", qos=1, retain=True
        )

        self.mqtt_client.on_disconnect = self._on_disconnect

        self.mqtt_client.reconnect_delay_set(min_delay=1, max_delay=32)
        if self.receiver_method is not None:
            self.mqtt_client.on_message = self.receiver_method
        self.mqtt_client.username_pw_set(
            self.config["user"],
            self.config["PW"],
        )
        if "cert_file" in self.config:
            self.mqtt_client.tls_set(os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", self.config["cert_file"]))
        # self.mqtt_client.tls_set("ca.crt")
        # self.mqtt_client.tls_insecure_set(False)
        self.mqtt_client.on_connect = self._on_connect
        self.mqtt_client.connect(
            host=self.config["broker_ip"],
            port=self.config["broker_port"],
        )
        self.mqtt_client.loop_start()
        # self.mqtt_client.publish(f"equipment/{self.name}/status", 'online', qos=1, retain=True)

    def send_mqtt_data(self):
        try:
            if not self.mqtt_client.is_connected():
                self.mqtt_client.reconnect()
            json_data = json.dumps(self.mqtt_data)
            self.mqtt_client.publish(self.mqtt_topic, json_data)
        except Exception:
            logger.exception("Error Sending date to mqtt_client - no retry")

    def send_data(self, parsed_data, **kwargs):
        if self.mqtt_client is not None:
            self.mqtt_data.update(
                {
                    key: value
                    for key, value in parsed_data.items()
                    if key not in self.suppress_zeros
                }
            )
            # self.mqtt_data.update(accumulated_data)
            self.mqtt_data.update(kwargs)
            self.send_mqtt_data()

    def handle_mqtt_averages(self, averaged_data):
        if self.mqtt_client is not None:
            self.mqtt_data.update(
                {
                    key: value
                    for key, value in averaged_data.items()
                    if key in self.suppress_zeros
                }
            )
            self.send_mqtt_data()
