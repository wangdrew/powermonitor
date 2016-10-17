__author__ = 'andrewwang'


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