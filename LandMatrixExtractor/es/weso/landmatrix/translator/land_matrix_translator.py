'''
Created on 22/01/2014

@author: Dani
'''

#from ConfigParser import ConfigParser
from lpentities.observation import Observation
from lpentities.value import Value
from lpentities.indicator import Indicator
from lpentities.computation import Computation
from lpentities.instant import Instant
from lpentities.measurement_unit import MeasurementUnit
from lpentities.dataset import Dataset
from lpentities.user import User
from lpentities.data_source import DataSource
from lpentities.license import License
from lpentities.organization import Organization
from lpentities.month_interval import MonthInterval

try:
    import xml.etree.cElementTree as ETree
except:
    import xml.etree.ElementTree as ETree

import codecs

class LandMatrixTranslator(object):
    '''
    classdocs
    '''

    INFO_NODE = "item"

    def __init__(self, log, config):
        """
        Constructor

        """
        self._log = log
        self._config = config

        #Initializing variable ids
        self._org_id = self._config.get("TRANSLATOR", "org_id")
        self._obs_int = int(self._config.get("TRANSLATOR", "obs_int"))
        self._sli_int = int(self._config.get("TRANSLATOR", "sli_int"))
        self._dat_int = int(self._config.get("TRANSLATOR", "dat_int"))
        self._igr_int = int(self._config.get("TRANSLATOR", "igr_int"))
        self._ind_int = int(self._config.get("TRANSLATOR", "ind_int"))
        self._sou_int = int(self._config.get("TRANSLATOR", "sou_int"))

        #Indicators' dict
        self._indicators_dict = self._build_indicators_dict()

        #Common objects
        self._default_user = self._build_default_user()
        self._default_organization = self._build_default_organization()
        self._default_datasource = self._build_default_datasource()
        self._default_dataset = self._build_default_dataset()
        self._default_license = self._build_default_license()

        self._relate_common_objects()

    @staticmethod
    def _build_default_user():
        return User(user_login="LANDMATRIXIMPORTER")

    def _build_default_organization(self):
        result = Organization(chain_for_id=self._org_id)
        result.name = self._config.get("ORGANIZATION", "name")
        result.url = self._config.get("ORGANIZATION", "url")
        result.url_logo = self._config.get("ORGANIZATION", "url_logo")
        result.description = self._config.get("ORGANIZATION", "description")

        return result

    def _build_default_datasource(self):
        result = DataSource(chain_for_id=self._org_id, int_for_id=self._sou_int)
        self._sou_int += 1  # Update
        result.name = self._config.get("DATASOURCE", "name")
        return result

    def _build_default_dataset(self):
        result = Dataset(chain_for_id=self._org_id, int_for_id=self._dat_int)
        self._dat_int += 1  # Needed increment
        result.frequency = Dataset.YEARLY  # TODO: a lie! The web says that it updates "frequently". No idea...
        return result

    def _build_default_license(self):
        result = License()
        result.republish = self._config.get("LICENSE", "republish")
        result.description = self._config.get("LICENSE", "description")
        result.name = self._config.get("LICENSE", "name")
        result.url = self._config.get("LICENSE", "url")

        return result

    def _relate_common_objects(self):
        self._default_organization.add_user(self._default_user)
        self._default_organization.add_data_source(self._default_datasource)
        self._default_datasource.add_dataset(self._default_dataset)
        self._default_dataset.license_type = self._default_license
        #No return needed


    def _build_indicators_dict(self):
        result = {}
        #TODO: Build something! We are not building a fuck =)
        return result


    def run(self, look_for_historical):
        """
        Translates the downloaded data into model objects. look_for_historical is a boolean
        that indicates if we have to consider old information or only bear in mind actual one

        """
        info_nodes = self._get_info_nodes_from_file()
        deals = self._turn_info_nodes_into_deals(info_nodes)


    def _turn_info_nodes_into_deals(self, info_nodes):
        result = []
        for info_node in info_nodes:
            a_deal = Deal()
        return result

    def _get_info_nodes_from_file(self):
        """
        Return a list of node objects that contains

        """
        xml_tree = ETree.parse(self._config.get("LAND_MATRIX", "target_file"))
        return xml_tree.findall(self.INFO_NODE)

    
    