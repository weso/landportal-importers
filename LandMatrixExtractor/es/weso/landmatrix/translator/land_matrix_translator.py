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
from es.weso.landmatrix.translator.deals_builder import DealsBuilder

try:
    import xml.etree.cElementTree as ETree
except:
    import xml.etree.ElementTree as ETree


class LandMatrixTranslator(object):
    '''
    classdocs
    '''

    INFO_NODE = "item"

    #INDICATOR KEYS
    TOTAL_DEALS = 0
    AGRICULTURE_DEALS = 1
    CONSERVATION_DEALS = 2
    INDUSTRY_DEALS = 3
    RENEWABLE_ENERGY_DEALS = 4
    TOURISM_DEALS = 5
    OTHER_DEALS = 6
    UNKNOWN_DEALS = 7
    FORESTRY_DEALS = 99

    INTENDED_DEALS = 8
    CONCLUDED_DEALS = 9
    FAILED_DEALS = 10

    HECTARES_TOTAL_DEALS = 11
    HECTARES_INTENDED_DEALS = 12
    HECTARES_CONTRACT_DEALS = 13
    HECTARES_PRODUCTION_DEALS = 14


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


    def run(self, look_for_historical):
        """
        Translates the downloaded data into model objects. look_for_historical is a boolean
        that indicates if we have to consider old information or only bear in mind actual one

        """
        info_nodes = self._get_info_nodes_from_file()
        deals = self._turn_info_nodes_into_deals(info_nodes)


    def f(self, info_nodes):
        result = []
        for info_node in info_nodes:
            result.append(DealsBuilder.turn_node_into_deal_object(info_node))
        return result

    def _get_info_nodes_from_file(self):
        """
        Return a list of node objects that contains

        """
        xml_tree = ETree.parse(self._config.get("LAND_MATRIX", "target_file"))
        return xml_tree.findall(self.INFO_NODE)


    def _build_indicators_dict(self):

        # Possibilities. Putting this ugly and huge code here, or refactor it, charging properties using
        # patterns: *_name_en, *_name_fr...
        # If i do that, we will have much less code, but we must to ensure that the property names never change.
        # I am not sure of which one is the most dangerous option, but also i'm not sure about if
        # that is a question that deserves to waste time with it. So huge and ugly code.


        hectares = MeasurementUnit("hectares")
        units = MeasurementUnit("units")

        result = {}

        #TOTAL DEALS
        total_deals = Indicator(chain_for_id=self._org_id, int_for_id=self._ind_int)
        self._ind_int += 1  # Updating id value
        total_deals.name_en = self._config.get("INDICATORS", "total_deals_name_en")
        total_deals.name_es = self._config.get("INDICATORS", "total_deals_name_es")
        total_deals.name_fr = self._config.get("INDICATORS", "total_deals_name_fr")
        total_deals.description_en = self._config.get("INDICATORS", "total_deals_desc_en")
        total_deals.description_es = self._config.get("INDICATORS", "total_deals_desc_es")
        total_deals.description_fr = self._config.get("INDICATORS", "total_deals_desc_fr")
        total_deals.topic = Indicator.TOPIC_TEMPORAL
        total_deals.measurement_unit = units
        total_deals.preferable_tendency = Indicator.IRRELEVANT
        result[self.TOTAL_DEALS] = total_deals


        #BY TOPIC
        #Agriculture
        agriculture_deals = Indicator(chain_for_id=self._org_id, int_for_id=self._ind_int)
        self._ind_int += 1  # Updating id value
        agriculture_deals.name_en = self._config.get("INDICATORS", "agriculture_deals_name_en")
        agriculture_deals.name_es = self._config.get("INDICATORS", "agriculture_deals_name_es")
        agriculture_deals.name_fr = self._config.get("INDICATORS", "agriculture_deals_name_fr")
        agriculture_deals.description_en = self._config.get("INDICATORS", "agriculture_deals_desc_en")
        agriculture_deals.description_es = self._config.get("INDICATORS", "agriculture_deals_desc_es")
        agriculture_deals.description_fr = self._config.get("INDICATORS", "agriculture_deals_desc_fr")
        agriculture_deals.topic = Indicator.TOPIC_TEMPORAL
        agriculture_deals.measurement_unit = units
        agriculture_deals.preferable_tendency = Indicator.IRRELEVANT
        result[self.AGRICULTURE_DEALS] = agriculture_deals

        #Conservation
        conservation_deals = Indicator(chain_for_id=self._org_id, int_for_id=self._ind_int)
        self._ind_int += 1  # Updating id value
        conservation_deals.name_en = self._config.get("INDICATORS", "conservation_deals_name_en")
        conservation_deals.name_es = self._config.get("INDICATORS", "conservation_deals_name_es")
        conservation_deals.name_fr = self._config.get("INDICATORS", "conservation_deals_name_fr")
        conservation_deals.description_en = self._config.get("INDICATORS", "conservation_deals_desc_en")
        conservation_deals.description_es = self._config.get("INDICATORS", "conservation_deals_desc_es")
        conservation_deals.description_fr = self._config.get("INDICATORS", "conservation_deals_desc_fr")
        conservation_deals.topic = Indicator.TOPIC_TEMPORAL
        conservation_deals.measurement_unit = units
        conservation_deals.preferable_tendency = Indicator.IRRELEVANT
        result[self.CONSERVATION_DEALS] = conservation_deals
        
        #Forestry
        forestry_deals = Indicator(chain_for_id=self._org_id, int_for_id=self._ind_int)
        self._ind_int += 1  # Updating id value
        forestry_deals.name_en = self._config.get("INDICATORS", "forestry_deals_name_en")
        forestry_deals.name_es = self._config.get("INDICATORS", "forestry_deals_name_es")
        forestry_deals.name_fr = self._config.get("INDICATORS", "forestry_deals_name_fr")
        forestry_deals.description_en = self._config.get("INDICATORS", "forestry_deals_desc_en")
        forestry_deals.description_es = self._config.get("INDICATORS", "forestry_deals_desc_es")
        forestry_deals.description_fr = self._config.get("INDICATORS", "forestry_deals_desc_fr")
        forestry_deals.topic = Indicator.TOPIC_TEMPORAL
        forestry_deals.measurement_unit = units
        forestry_deals.preferable_tendency = Indicator.IRRELEVANT
        result[self.FORESTRY_DEALS] = forestry_deals
        
        #Industry
        industry_deals = Indicator(chain_for_id=self._org_id, int_for_id=self._ind_int)
        self._ind_int += 1  # Updating id value
        industry_deals.name_en = self._config.get("INDICATORS", "industry_deals_name_en")
        industry_deals.name_es = self._config.get("INDICATORS", "industry_deals_name_es")
        industry_deals.name_fr = self._config.get("INDICATORS", "industry_deals_name_fr")
        industry_deals.description_en = self._config.get("INDICATORS", "industry_deals_desc_en")
        industry_deals.description_es = self._config.get("INDICATORS", "industry_deals_desc_es")
        industry_deals.description_fr = self._config.get("INDICATORS", "industry_deals_desc_fr")
        industry_deals.topic = Indicator.TOPIC_TEMPORAL
        industry_deals.measurement_unit = units
        industry_deals.preferable_tendency = Indicator.IRRELEVANT
        result[self.INDUSTRY_DEALS] = industry_deals
        
        #Renewable energy
        renewable_energy_deals = Indicator(chain_for_id=self._org_id, int_for_id=self._ind_int)
        self._ind_int += 1  # Updating id value
        renewable_energy_deals.name_en = self._config.get("INDICATORS", "renewable_energy_deals_name_en")
        renewable_energy_deals.name_es = self._config.get("INDICATORS", "renewable_energy_deals_name_es")
        renewable_energy_deals.name_fr = self._config.get("INDICATORS", "renewable_energy_deals_name_fr")
        renewable_energy_deals.description_en = self._config.get("INDICATORS", "renewable_energy_deals_desc_en")
        renewable_energy_deals.description_es = self._config.get("INDICATORS", "renewable_energy_deals_desc_es")
        renewable_energy_deals.description_fr = self._config.get("INDICATORS", "renewable_energy_deals_desc_fr")
        renewable_energy_deals.topic = Indicator.TOPIC_TEMPORAL
        renewable_energy_deals.measurement_unit = units
        renewable_energy_deals.preferable_tendency = Indicator.IRRELEVANT
        result[self.RENEWABLE_ENERGY_DEALS] = renewable_energy_deals
        
        #Tourism
        tourism_deals = Indicator(chain_for_id=self._org_id, int_for_id=self._ind_int)
        self._ind_int += 1  # Updating id value
        tourism_deals.name_en = self._config.get("INDICATORS", "tourism_deals_name_en")
        tourism_deals.name_es = self._config.get("INDICATORS", "tourism_deals_name_es")
        tourism_deals.name_fr = self._config.get("INDICATORS", "tourism_deals_name_fr")
        tourism_deals.description_en = self._config.get("INDICATORS", "tourism_deals_desc_en")
        tourism_deals.description_es = self._config.get("INDICATORS", "tourism_deals_desc_es")
        tourism_deals.description_fr = self._config.get("INDICATORS", "tourism_deals_desc_fr")
        tourism_deals.topic = Indicator.TOPIC_TEMPORAL
        tourism_deals.measurement_unit = units
        tourism_deals.preferable_tendency = Indicator.IRRELEVANT
        result[self.TOURISM_DEALS] = tourism_deals
        
        #Other
        other_topic_deals = Indicator(chain_for_id=self._org_id, int_for_id=self._ind_int)
        self._ind_int += 1  # Updating id value
        other_topic_deals.name_en = self._config.get("INDICATORS", "other_topic_deals_name_en")
        other_topic_deals.name_es = self._config.get("INDICATORS", "other_topic_deals_name_es")
        other_topic_deals.name_fr = self._config.get("INDICATORS", "other_topic_deals_name_fr")
        other_topic_deals.description_en = self._config.get("INDICATORS", "other_topic_deals_desc_en")
        other_topic_deals.description_es = self._config.get("INDICATORS", "other_topic_deals_desc_es")
        other_topic_deals.description_fr = self._config.get("INDICATORS", "other_topic_deals_desc_fr")
        other_topic_deals.topic = Indicator.TOPIC_TEMPORAL
        other_topic_deals.measurement_unit = units
        other_topic_deals.preferable_tendency = Indicator.IRRELEVANT
        result[self.OTHER_DEALS] = other_topic_deals
        
        #Unknown
        unknown_topic_deals = Indicator(chain_for_id=self._org_id, int_for_id=self._ind_int)
        self._ind_int += 1  # Updating id value
        unknown_topic_deals.name_en = self._config.get("INDICATORS", "unknown_topic_deals_name_en")
        unknown_topic_deals.name_es = self._config.get("INDICATORS", "unknown_topic_deals_name_es")
        unknown_topic_deals.name_fr = self._config.get("INDICATORS", "unknown_topic_deals_name_fr")
        unknown_topic_deals.description_en = self._config.get("INDICATORS", "unknown_topic_deals_desc_en")
        unknown_topic_deals.description_es = self._config.get("INDICATORS", "unknown_topic_deals_desc_es")
        unknown_topic_deals.description_fr = self._config.get("INDICATORS", "unknown_topic_deals_desc_fr")
        unknown_topic_deals.topic = Indicator.TOPIC_TEMPORAL
        unknown_topic_deals.measurement_unit = units
        unknown_topic_deals.preferable_tendency = Indicator.IRRELEVANT
        result[self.UNKNOWN_DEALS] = unknown_topic_deals

        #BY NEGOTIATION STATUS
        #Intended
        intended_deals = Indicator(chain_for_id=self._org_id, int_for_id=self._ind_int)
        self._ind_int += 1  # Updating id value
        intended_deals.name_en = self._config.get("INDICATORS", "intended_deals_name_en")
        intended_deals.name_es = self._config.get("INDICATORS", "intended_deals_name_es")
        intended_deals.name_fr = self._config.get("INDICATORS", "intended_deals_name_fr")
        intended_deals.description_en = self._config.get("INDICATORS", "intended_deals_desc_en")
        intended_deals.description_es = self._config.get("INDICATORS", "intended_deals_desc_es")
        intended_deals.description_fr = self._config.get("INDICATORS", "intended_deals_desc_fr")
        intended_deals.topic = Indicator.TOPIC_TEMPORAL
        intended_deals.measurement_unit = units
        intended_deals.preferable_tendency = Indicator.IRRELEVANT
        result[self.INTENDED_DEALS] = intended_deals

        #Concluded
        concluded_deals = Indicator(chain_for_id=self._org_id, int_for_id=self._ind_int)
        self._ind_int += 1  # Updating id value
        concluded_deals.name_en = self._config.get("INDICATORS", "concluded_deals_name_en")
        concluded_deals.name_es = self._config.get("INDICATORS", "concluded_deals_name_es")
        concluded_deals.name_fr = self._config.get("INDICATORS", "concluded_deals_name_fr")
        concluded_deals.description_en = self._config.get("INDICATORS", "concluded_deals_desc_en")
        concluded_deals.description_es = self._config.get("INDICATORS", "concluded_deals_desc_es")
        concluded_deals.description_fr = self._config.get("INDICATORS", "concluded_deals_desc_fr")
        concluded_deals.topic = Indicator.TOPIC_TEMPORAL
        concluded_deals.measurement_unit = units
        concluded_deals.preferable_tendency = Indicator.IRRELEVANT
        result[self.CONCLUDED_DEALS] = concluded_deals
        
        #Failed
        failed_deals = Indicator(chain_for_id=self._org_id, int_for_id=self._ind_int)
        self._ind_int += 1  # Updating id value
        failed_deals.name_en = self._config.get("INDICATORS", "failed_deals_name_en")
        failed_deals.name_es = self._config.get("INDICATORS", "failed_deals_name_es")
        failed_deals.name_fr = self._config.get("INDICATORS", "failed_deals_name_fr")
        failed_deals.description_en = self._config.get("INDICATORS", "failed_deals_desc_en")
        failed_deals.description_es = self._config.get("INDICATORS", "failed_deals_desc_es")
        failed_deals.description_fr = self._config.get("INDICATORS", "failed_deals_desc_fr")
        failed_deals.topic = Indicator.TOPIC_TEMPORAL
        failed_deals.measurement_unit = units
        failed_deals.preferable_tendency = Indicator.IRRELEVANT
        result[self.FAILED_DEALS] = failed_deals

        #ABOUT HECTARES
        #Total hectares
        hectares_total_deals = Indicator(chain_for_id=self._org_id, int_for_id=self._ind_int)
        self._ind_int += 1  # Updating id value
        hectares_total_deals.name_en = self._config.get("INDICATORS", "hectares_total_deals_name_en")
        hectares_total_deals.name_es = self._config.get("INDICATORS", "hectares_total_deals_name_es")
        hectares_total_deals.name_fr = self._config.get("INDICATORS", "hectares_total_deals_name_fr")
        hectares_total_deals.description_en = self._config.get("INDICATORS", "hectares_total_deals_desc_en")
        hectares_total_deals.description_es = self._config.get("INDICATORS", "hectares_total_deals_desc_es")
        hectares_total_deals.description_fr = self._config.get("INDICATORS", "hectares_total_deals_desc_fr")
        hectares_total_deals.topic = Indicator.TOPIC_TEMPORAL
        hectares_total_deals.measurement_unit = hectares
        hectares_total_deals.preferable_tendency = Indicator.IRRELEVANT
        result[self.HECTARES_TOTAL_DEALS] = hectares_total_deals
        
        #intended hectares
        hectares_intended_deals = Indicator(chain_for_id=self._org_id, int_for_id=self._ind_int)
        self._ind_int += 1  # Updating id value
        hectares_intended_deals.name_en = self._config.get("INDICATORS", "hectares_intended_deals_name_en")
        hectares_intended_deals.name_es = self._config.get("INDICATORS", "hectares_intended_deals_name_es")
        hectares_intended_deals.name_fr = self._config.get("INDICATORS", "hectares_intended_deals_name_fr")
        hectares_intended_deals.description_en = self._config.get("INDICATORS", "hectares_intended_deals_desc_en")
        hectares_intended_deals.description_es = self._config.get("INDICATORS", "hectares_intended_deals_desc_es")
        hectares_intended_deals.description_fr = self._config.get("INDICATORS", "hectares_intended_deals_desc_fr")
        hectares_intended_deals.topic = Indicator.TOPIC_TEMPORAL
        hectares_intended_deals.measurement_unit = hectares
        hectares_intended_deals.preferable_tendency = Indicator.IRRELEVANT
        result[self.HECTARES_INTENDED_DEALS] = hectares_intended_deals

        #contract hectares
        hectares_contract_deals = Indicator(chain_for_id=self._org_id, int_for_id=self._ind_int)
        self._ind_int += 1  # Updating id value
        hectares_contract_deals.name_en = self._config.get("INDICATORS", "hectares_contract_deals_name_en")
        hectares_contract_deals.name_es = self._config.get("INDICATORS", "hectares_contract_deals_name_es")
        hectares_contract_deals.name_fr = self._config.get("INDICATORS", "hectares_contract_deals_name_fr")
        hectares_contract_deals.description_en = self._config.get("INDICATORS", "hectares_contract_deals_desc_en")
        hectares_contract_deals.description_es = self._config.get("INDICATORS", "hectares_contract_deals_desc_es")
        hectares_contract_deals.description_fr = self._config.get("INDICATORS", "hectares_contract_deals_desc_fr")
        hectares_contract_deals.topic = Indicator.TOPIC_TEMPORAL
        hectares_contract_deals.measurement_unit = hectares
        hectares_contract_deals.preferable_tendency = Indicator.IRRELEVANT
        result[self.HECTARES_CONTRACT_DEALS] = hectares_contract_deals

        #production hectares
        hectares_production_deals = Indicator(chain_for_id=self._org_id, int_for_id=self._ind_int)
        self._ind_int += 1  # Updating id value
        hectares_production_deals.name_en = self._config.get("INDICATORS", "hectares_production_deals_name_en")
        hectares_production_deals.name_es = self._config.get("INDICATORS", "hectares_production_deals_name_es")
        hectares_production_deals.name_fr = self._config.get("INDICATORS", "hectares_production_deals_name_fr")
        hectares_production_deals.description_en = self._config.get("INDICATORS", "hectares_production_deals_desc_en")
        hectares_production_deals.description_es = self._config.get("INDICATORS", "hectares_production_deals_desc_es")
        hectares_production_deals.description_fr = self._config.get("INDICATORS", "hectares_production_deals_desc_fr")
        hectares_production_deals.topic = Indicator.TOPIC_TEMPORAL
        hectares_production_deals.measurement_unit = hectares
        hectares_production_deals.preferable_tendency = Indicator.IRRELEVANT
        result[self.HECTARES_PRODUCTION_DEALS] = hectares_production_deals

        #And, at last, return the dict
        return result
    
    