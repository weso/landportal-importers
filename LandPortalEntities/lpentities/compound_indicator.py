__author__ = 'Dani Fdez'

from .indicator import Indicator


class CompoundIndicator(Indicator):
    def __init__(self, indicator_id=None, name=None, description=None,
                 dataset=None, measurement_unit=None, indicators=None):
        super(CompoundIndicator, self).__init__(indicator_id, name, description,
                                                dataset, measurement_unit)

        self.indicators = indicators

    def add_indicator(self, indicator):
        self.indicators.append(indicator)