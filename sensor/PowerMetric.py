__author__ = 'andrewwang'


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
