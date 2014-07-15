from datetime import datetime
from lpentities.computation import Computation
from random import randint
from lpentities.country import Country

from lpentities.dataset import Dataset
from lpentities.indicator import Indicator
from lpentities.instant import Instant
from lpentities.license import License
from lpentities.measurement_unit import MeasurementUnit
from lpentities.observation import Observation
from lpentities.user import User
from lpentities.organization import Organization
from lpentities.data_source import DataSource
from lpentities.year_interval import YearInterval
from lpentities.value import Value
from model2xml.model2xml import ModelToXMLTransformer, XmlSplitter

import os

try:
    import xml.etree.cElementTree as ETree
except:
    import xml.etree.ElementTree as ETree

__author__ = 'Dani'

import unittest


class ModelToXmlTest(unittest.TestCase):
    def setUp(self):
        #import_process
        self.import_process = "Excell"

        #User
        self.user = User("PWESO")

        #Organization
        self.organization = Organization(chain_for_id="a_ch")
        self.organization.name = "Weso"
        self.organization.url = "http://weso.test.org"
        self.organization.add_user(self.user)

        #Datasource
        self.datasource = DataSource(chain_for_id="wes")
        self.datasource.name = "WesoPortal"
        self.organization.add_data_source(self.datasource)

        #Dataset
        self.dataset = Dataset(int_for_id=1, chain_for_id="a_ch")
        self.dataset.name = "WESOStat"
        self.dataset.frequency = "http://a.frequence.inaplace#some"
        self.datasource.add_dataset(self.dataset)

        #Transformer
        self.transformer = ModelToXMLTransformer(self.dataset, self.import_process, self.user)

    ########## TEST
    def test_build_import_process_node(self):
        self.transformer.build_import_process_node()
        node = self.transformer._root.find(ModelToXMLTransformer.IMPORT_PROCESS)

        self.assertIsNotNone(node)
        self.assertEquals(len(node.getchildren()), 6)

    ########## TEST
    def test_obs_conservation(self):
        user, dataset = self._generate_random_model(10000)
        transformer = ModelToXmlForTest(dataset, "doesntmatter", user)
        paths = transformer.run()
        self.assert_number_of_obs_in_paths(paths, 10000)
        self._remove_files(paths)

    ######## TEST
    def test_splitter_obs_conservation(self):
        user, dataset = self._generate_random_model(100000)
        old_max_obs = XmlSplitter._MAX_OBSERVATIONS_ALLOWED
        XmlSplitter._MAX_OBSERVATIONS_ALLOWED = 23000
        transformer = ModelToXmlForTest(dataset, "doesntmatter", user)
        paths = transformer.run()
        print len(paths)
        XmlSplitter._MAX_OBSERVATIONS_ALLOWED = old_max_obs
        self.assert_number_of_obs_in_paths(paths, 100000)
        self._remove_files(paths)

        #TODO


    def _remove_files(self, paths):
        for a_path in paths:
            os.remove(a_path)

    def assert_number_of_obs_in_paths(self, paths, target_number_of_obs):
        total_obs = 0
        for a_path in paths:
            total_obs += self.get_number_of_obs_in_path(a_path)
        self.assertEquals(total_obs, target_number_of_obs)

    def get_number_of_obs_in_path(self, a_path):
        with open(a_path) as file_obj:
            file_content = file_obj.read()
            tree = ETree.fromstring(file_content)
            obs_node = XmlSplitter._get_observations_node_of_a_tree(tree)
            return len(obs_node.getchildren())



    def _generate_random_model(self, num_obs):
        user = User("a_user")
        organization = Organization("a_org")
        organization.add_user(user)
        datasource = DataSource(chain_for_id="a_org", int_for_id=1, name="a_sou")
        organization.add_data_source(datasource)
        dataset = Dataset(chain_for_id="a_org", int_for_id=1)
        datasource.add_dataset(dataset)
        license_ob = License("a", "b", True, "c")
        dataset.license_type = license_ob

        indicator = Indicator(int_for_id=1, chain_for_id="a_org")
        indicator.topic = 'CLIMATE_CHANGE'
        indicator.preferable_tendency = Indicator.IRRELEVANT
        indicator.name_en = "a"
        indicator.name_es = "a"
        indicator.name_fr = "a"
        indicator.description_en = "b"
        indicator.description_es = "b"
        indicator.description_fr = "b"
        indicator.measurement_unit = MeasurementUnit(name="a_name", convert_to=MeasurementUnit.RANK, factor=1)

        country = Country(name="a_country", is_part_of=None, iso3="XXX", iso2="XX")


        for i in range(0, num_obs):
            dataset.add_observation(self._generate_random_observation(i, indicator, country))

        return user, dataset

    def _generate_random_observation(self, obs_id, indicator, country):

        result = Observation(chain_for_id="a_org", int_for_id=obs_id)
        result.computation = Computation(uri=Computation.RAW)
        result.indicator = indicator
        result.issued = Instant(datetime.now())
        result.ref_time = YearInterval(2013)
        result.value = Value(randint(1, 50000), Value.INTEGER, Value.AVAILABLE)
        country.add_observation(result)

        return result







if __name__ == '__main__':
    unittest.main()


class ModelToXmlForTest(ModelToXMLTransformer, object):

    def __init__(self, dataset, import_process, user, indicator_relations=None):
        super(ModelToXMLTransformer, self).__init__()
        self._datasource = dataset.source
        self._dataset = dataset
        self._user = user
        self._import_process = import_process
        self._root = None
        self._indicator_dic = {}  # It will store an indicator object with it id as key.
        self._group_dic = {}
        self._indicator_relations = indicator_relations

        self._root = self._build_root()


    def run(self):
        # Same as the super method, but returns the paths to the files
        self.build_import_process_node()  # Done
        self.build_license_node()  # Done
        self.build_observations_node()  # Done
        self.build_indicators_node()  # Done
        self.build_indicator_groups_node()  # Done
        self.build_slices_node()  # Done
        self.include_indicator_relations()  # Done
        paths = self._persist_tree()  #
        return paths



