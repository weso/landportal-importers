__author__ = 'Dani'

from reconciler.country_reconciler import CountryReconciler
from lpentities.dataset import Dataset

import os
try:
    import xml.etree.cElementTree as ET
except:
    import xml.etree.ElementTree as ET

class UNDPTranslator(object):


    BASE_ROW = "row"

    def __init__(self, config, log):
        self.config = config
        self.log = log
        self.reconciler = CountryReconciler()
        self.datasets = []

        self._org_id = self.config.get("TRANSLATOR", "org_id")
        self._obs_int = int(self.config.get("TRANSLATOR", "obs_int"))
        self._sli_int = int(self.config.get("TRANSLATOR", "sli_int"))
        self._dat_int = int(self.config.get("TRANSLATOR", "dat_int"))
        self._igr_int = int(self.config.get("TRANSLATOR", "igr_int"))
        self._ind_int = int(self.config.get("TRANSLATOR", "ind_int"))
        self._sou_int = int(self.config.get("TRANSLATOR", "sou_int"))


    def run(self):
        """
        Steps:
         - Turn file into an xml object in memory
         - Turn that object into model landportal objects
         - Turn model objects into a xml per dataset and send it to the receiver

        """
        available_table_trees = self._turn_file_tables_into_xml_objects()
        for tree in available_table_trees:
            self.datasets.append(self._create_dataset_from_table(tree))

        for dataset in self.datasets:
            self._decorate_dataset_with_common_objects(dataset)
            self._generate_xml_from_dataset_model(dataset)

    def _create_dataset_from_table(self, tree):
        dataset = self._create_empty_dataset()
        base_node = tree.getroot().find(self.BASE_ROW)
        for country_node in base_node.getchildren():
            self._add_country_info_to_dataset_from_country_node(dataset, country_node)
        return dataset

    def _add_country_info_to_dataset_from_country_node(self, dataset, country_node):
        valid_info_subnodes = self._filter_valid_info_subnodes(country_node)  # TODO: continue here!


    @staticmethod
    def _filter_valid_info_subnodes(country_node):
        result = []
        for subnode in country_node.getchildren():
            if not subnode.tag.startswith("_"):  # Country code and country name nodes
                result.append(subnode)
            elif subnode.tag.endswith("_hdi"):  # Concrete hdi data by year
                result.append(subnode)
            elif subnode.tag.endswith("_rank"): # HDI rank node
                result.append(subnode)
            #In any other cases, we will just ignore the node
        return result

    def _create_empty_dataset(self):
        dataset = Dataset(chain_for_id=self._org_id,
                          int_for_id=self._dat_int,
                          frequency=Dataset.YEARLY)
        self._dat_int += 1
        return dataset

        pass

    def _turn_file_tables_into_xml_objects(self):
        """
        It looks for xml files in a concrete directory, where the downloaded info is expected.
        Then turn that info in xml objects in memory

        """
        result = []
        base_directory = self.config.get("TRANSLATOR", "downloaded_data")
        candidate_files = os.listdir(base_directory)
        for candidate_file in candidate_files:
            if os.path.splitext(candidate_file)[1] == "xml":
                result.append(self._turn_table_file_into_xml_object(candidate_file))
        return result

    @staticmethod
    def _turn_table_file_into_xml_object(file_path):
        try:
            return ET.parse(file_path)
        except:
            raise RuntimeError("Impossible to parse xml in path: {0}. \
                    It looks that it is not a valid xml file.".format(str(file_path)))


