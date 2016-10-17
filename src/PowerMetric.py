__author__ = 'andrewwang'

import json

class PowerMetric():
    def __init__(self,
                 voltageV = None,
                 currentA = None,
                 powerW = None,
                 powerUsedKwh = None,
                 dailyCost = None,
                 cumCost = None):
        self.voltageV = voltageV
        self.currentA = currentA
        self.powerW = powerW
        self.powerUsedKwh = powerUsedKwh
        self.dailyCost = dailyCost
        self.cumCost = cumCost


    @staticmethod
    def from_json(json_string):
        map = json.loads(json_string)
        try:
            return PowerMetric(map['voltageV'], map['currentA'], map['powerW'],
                               map['powerUsedKwh'], map['dailyCost'], map['cumCost'])
        except Exception as e:
            print "Error extracting deserializing PowerMetric from JSON. %s" % str(e)


    def to_json(self):
        return json.dumps(self.as_dict())

    def as_dict(self):
        return {'voltageV': self.voltageV,
                'currentA': self.currentA,
                'powerW': self.powerW,
                'powerUsedKwh': self.powerUsedKwh,
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