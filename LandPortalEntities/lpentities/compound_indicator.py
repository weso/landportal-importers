__author__ = 'Dani Fdez'

from .indicator import Indicator


class CompoundIndicator(Indicator):

    def __init__(self, chain_for_id, int_for_id, name_en=None, name_es=None,
                 name_fr=None, description_en=None, description_es=None, description_fr=None,
                 dataset=None, measurement_unit=None, indicators=None):
        super(CompoundIndicator, self).__init__(chain_for_id, int_for_id, name_en, name_es,
                                                name_fr, description_en, description_es, description_fr,
                                                dataset, measurement_unit)

        self.indicators = indicators

    def add_indicator(self, indicator):
        self.indicators.append(indicator)