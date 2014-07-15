__author__ = 'Dani'


class XmlRegister(object):


    def __init__(self, year=None, month=None, titres_crees=None, mutations=None,
                 csj=None, reperages=None, bornages=None, reproduction_des_plans=None):
        self.year = year
        self.month = month
        self.titres_crees = titres_crees
        self.mutations = mutations
        self.csj = csj
        self.reperages = reperages
        self.bornages = bornages
        self.reproduction_des_plans = reproduction_des_plans

