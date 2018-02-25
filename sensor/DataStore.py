__author__ = 'andrewwang'

import requests
import copy
import time
import json
import paho.mqtt.client as mqtt
import paho.mqtt.publish as mqtt_publish


class DataStore():
    def __init__(self):
        pass

    # Implement this
    def write_to_store(self, power_metric):
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


class PowerMetric():
    def __init__(self,
                 voltageV = None,
                 currentA = None,
                 powerW = None,
                 powerAux1W = None,
                 powerAux2W = None,
                 powerAux3W = None,
                 powerUsedKwh = None,
                 powerUsedAux1Kwh = None,
                 powerUsedAux2Kwh = None,
                 powerUsedAux3Kwh = None,
                 dailyCost = None,
                 cumCost = None):
        self.voltageV = voltageV
        self.currentA = currentA
        self.powerW = powerW
        self.powerAux1W = powerAux1W
        self.powerAux2W = powerAux2W
        self.powerAux3W = powerAux3W
        self.powerUsedKwh = powerUsedKwh
        self.powerUsedAux1Kwh = powerUsedAux1Kwh
        self.powerUsedAux2Kwh = powerUsedAux2Kwh
        self.powerUsedAux3Kwh = powerUsedAux3Kwh
        self.dailyCost = dailyCost
        self.cumCost = cumCost

    def as_dict(self):
        return {'voltageV': self.voltageV,
                'currentA': self.currentA,
                'powerW': self.powerW,
                'powerAux1W': self.powerAux1W,
                'powerAux2W': self.powerAux2W,
                'powerAux3W': self.powerAux3W,
                'powerUsedKwh': self.powerUsedKwh,
                'powerUsedAux1Kwh': self.powerUsedAux1Kwh,
                'powerUsedAux2Kwh': self.powerUsedAux2Kwh,
                'powerUsedAux3Kwh': self.powerUsedAux3Kwh,
                'dailyCost': self.dailyCost,
                'cumCost': self.cumCost}

    def __iter__(self):
        d = self.as_dict()
        for key in d:
            yield (key, d[key])

    def __repr__(self):
        return str(self.as_dict())

    def __str__(self):
        return str(self.as_dict())
