'''
Created on 19/12/2013

@author: Nacho
'''


class Indicator(object):

    TOPIC_CLIMATE_CHANGE = "TOP1"
    TOPIC_COUNTRY_DATA = "TOP2"
    TOPIC_FOOD_SEC_AND_HUNGER = "TOP3"
    TOPIC_LAND_AND_GENDER = "TOP4"
    TOPIC_LAND_TENURE = "TOP5"
    TOPIC_SOCIO_ECONOMIC_AND_POVERTY = "TOP6"
    TOPIC_USAGE_AND_INVESTMENT = "TOP7"

    TOPIC_TEMPORAL = "TOP99"   # the finla topic list is still unknown. We will be using this for now

    '''
    classdocs
    '''

    def __init__(self, chain_for_id, int_for_id, name_en=None ,name_es=None,
                 name_fr=None, description_en=None, description_es=None,
                 description_fr=None, dataset=None, measurement_unit=None,
                 topic=None):
        '''
        Constructor
        '''
        self.name_en = name_en
        self.name_es = name_es
        self.name_fr = name_fr
        self.description_en = description_en
        self.description_es = description_es
        self.description_fr = description_fr
        self.dataset = dataset
        self.measurement_unit = measurement_unit
        self.topic = topic

        self.indicator_id = self._generate_id(chain_for_id, int_for_id)


    @staticmethod
    def _generate_id(chain_for_id, int_for_id):
        return "IND" + chain_for_id.upper() + str(int_for_id).upper()