'''
Created on 19/12/2013

@author: Nacho
'''
from lpentities.measurement_unit import MeasurementUnit


class Indicator(object):
    """
    classdocs

    """

    #Simulated Enum Values
    INCREASE = "increase"
    DECREASE = "decrease"
    IRRELEVANT = "irrelevant "

    #Possible topics
    _topics_set = ['CLIMATE_CHANGE', 'GEOGRAPH_SOCIO', 'LAND_USE', 'LAND_GENDER', 'LAND_TENURE', 'FSECURITY_HUNGER', 'TEMP_TOPIC']



    def __init__(self, chain_for_id, int_for_id, name_en=None, name_es=None,
                 name_fr=None, description_en=None, description_es=None,
                 description_fr=None, dataset=None, measurement_unit=None,
                 topic=None, preferable_tendency=None):
        """
        Constructor
        """
        self.name_en = name_en
        self.name_es = name_es
        self.name_fr = name_fr
        self.description_en = description_en
        self.description_es = description_es
        self.description_fr = description_fr
        self.dataset = dataset
        self._measurement_unit = measurement_unit
        self._topic = topic
        self._preferable_tendency = preferable_tendency

        self.indicator_id = self._generate_id(chain_for_id, int_for_id)

    
    def __get_measurement_unit(self):
        return self._measurement_unit
    
    def __set_measurement_unit(self, measurement_unit):
        if isinstance(measurement_unit, MeasurementUnit):
            self._measurement_unit = measurement_unit
        else:
            raise ValueError("Expected Measurement object in Indicator")
        
    measurement_unit = property(fget=__get_measurement_unit, fset=__set_measurement_unit, doc="MeasurementUnit of the indicator")
    
    def __get_topic(self):
        return self._topic
    
    def __set_topic(self, topic):
        if topic.upper() in self._topics_set:
            self._topic = topic
        else:
            raise ValueError("Provided topic not in the specified list")
        
    topic = property(fget=__get_topic, fset=__set_topic, doc="Topic of the indicator")
    
    def __get_preferable_tendency(self):
        return self._preferable_tendency
    
    def __set_preferable_tendency(self, preferable_tendency):
        if preferable_tendency == self.DECREASE or preferable_tendency == self.INCREASE or preferable_tendency == self.IRRELEVANT:
            self._preferable_tendency = preferable_tendency
        else:
            raise ValueError("Provided tendency not in the specified list")
        
    preferable_tendency = property(fget=__get_preferable_tendency, fset=__set_preferable_tendency, doc="Preferable tendency of the indicator")
    
    @staticmethod
    def _generate_id(chain_for_id, int_for_id):
        return "IND" + chain_for_id.upper() + str(int_for_id).upper()
