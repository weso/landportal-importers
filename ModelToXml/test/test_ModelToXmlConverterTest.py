from datetime import datetime

from lpentities.dataset import Dataset
from lpentities.user import User
from lpentities.organization import Organization
from lpentities.data_source import DataSource
from model2xml.model2xml import ModelToXMLTransformer


__author__ = 'Dani'

import unittest


class ModelToXmlTest(unittest.TestCase):

    def setUp(self):
        #import_process
        self.import_process = "Excell"

        #User
        self.user = User()
        self.user.user_id = "Mike"
        self.user.user_ip = "156.35.200.200"
        self.user.timestamp = datetime.now()

        #Organization
        self.organization = Organization()
        self.organization.name = "Weso"
        self.organization.url = "http://weso.test.org"
        self.user.organization = self.organization

        #Datasource
        self.datasource = DataSource()
        self.datasource.name = "WesoPortal"
        self.source_id = "wpt1"
        self.organization.add_data_source(self.datasource)

        #Dataset
        self.dataset = Dataset()
        self.dataset.name = "WESOStat"
        self.dataset.dataset_id = "datatest1"
        self.dataset.frequency = "http://a.frequence.inaplace#some"
        self.datasource.add_dataset(self.dataset)

        #Transformet
        self.transformer = ModelToXMLTransformer(self.dataset, self.import_process, self.user)

    def test_something(self):
        self.assertEquals(self.dataset.name, "WESOStat")

    def test_build_import_process_node(self):
        self.transformer.build_import_process_node()
        node = self.transformer._root.find(ModelToXMLTransformer.IMPORT_PROCESS)

        self.assertIsNotNone(node)
        self.assertEquals(len(node.getchildren()), 5)


if __name__ == '__main__':
    unittest.main()
