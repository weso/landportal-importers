__author__ = 'Dani Fdez'

from .indicator import Indicator


class CompoundIndicator(Indicator):

    def __init__(self, chain_for_id, int_for_id, name=None, description=None,
                 dataset=None, measurement_unit=None, indicators=None):
        super(CompoundIndicator, self).__init__(chain_for_id, int_for_id, name, description,
                                                dataset, measurement_unit)

        self.indicators = indicators

    def add_indicator(self, indicator):
        self.indicators.append(indicator)