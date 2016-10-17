__author__ = 'andrewwang'

import copy
from time
import json

import requests
import paho.mqtt.publish as mqtt_publish
from influxdb import InfluxDBClient


class DataStore():
    def __init__(self):
        pass

    # Implement this
    def write_to_store(self, power_metric):
        pass


class InfluxDbDataStore(DataStore):

    def __init__(self, influx_ip, influx_port, username, password, db_name):
        self.template_metric = {"measurement": "", "tags": {}, "time": "", "fields": {}}
        try:
            self.influxdb = InfluxDBClient(influx_ip, influx_port, username, password, db_name)
            self.influxdb.create_database(db_name)

        except Exception as e:
            print("Error initializing influx client : %s" % str(e))

    def write(self, power_metric):
# "2009-11-10T23:00:00Z",
        output = []
        ts = int(time.time()*1e6)
        for key in power_metric.as_dict().keys():
            datapoint = copy.deepcopy(self.template_metric)
            datapoint

    def read(self, power_metric):
        pass

class KairosDataStore(DataStore):
    def __init__(self, kairos_ip, kairos_port):
        self.url = "http://" + str(kairos_ip) + ":" + str(kairos_port) + "/api/v1/datapoints"
        self.template_metric = {
            "name": "",
            "timestamp": "",
            "value": "",
            "tags": {"channel": "0"},
            "type": "double"}

    def write_to_store(self, power_metric):
        metrics_to_db = []
        for metric_kv in power_metric:
            metric_body = copy.deepcopy(self.template_metric)
            metric_body["name"] = metric_kv[0]
            metric_body["timestamp"] = long(time.time() * 1000)
            metric_body["value"] = metric_kv[1]
            metrics_to_db.append(metric_body)

        resp = requests.post(self.url, data=json.dumps(metrics_to_db))
        if resp.status_code != 204:  # kairosDB success response code
            print resp.text


class MqttDataStore(DataStore):
    def __init__(self, mqtt_url, mqtt_port, topic_name):
        self.topic = str(topic_name)
        self.url = mqtt_url
        self.port = mqtt_port

    def write_to_store(self, power_metric):
        mqtt_publish.single(self.topic, payload=json.dumps(power_metric.as_dict()), hostname=self.url, port=self.port)


# TODO: implement later
class InfluxDataStore(DataStore):
    pass


