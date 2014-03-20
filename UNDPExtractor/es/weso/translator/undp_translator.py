# coding=utf-8
from reconciler.exceptions.unknown_country_error import UnknownCountryError

__author__ = 'Dani'

from reconciler.country_reconciler import CountryReconciler
from lpentities.dataset import Dataset
from lpentities.observation import Observation
from lpentities.indicator import Indicator
from lpentities.measurement_unit import MeasurementUnit
from lpentities.computation import Computation
from lpentities.instant import Instant
from lpentities.year_interval import YearInterval
from lpentities.value import Value
from lpentities.user import User
from lpentities.data_source import DataSource
from lpentities.organization import Organization
from lpentities.license import License
from model2xml.model2xml import ModelToXMLTransformer

import os
from datetime import datetime

try:
    import xml.etree.cElementTree as ETree
except:
    import xml.etree.ElementTree as ETree


class UNDPTranslator(object):
    BASE_ROW = "row"
    COUNTRY_CODE = "country_code"
    COUNTRY_NAME = "country_name"

    HDI_ENDING = "_hdi"
    RANK_ENDING = "_rank"

    def __init__(self, config, log):
        self._config = config
        self._log = log
        self._reconciler = CountryReconciler()

        #Getting propper ids
        self._org_id = self._config.get("TRANSLATOR", "org_id")
        self._obs_int = int(self._config.get("TRANSLATOR", "obs_int"))
        self._sli_int = int(self._config.get("TRANSLATOR", "sli_int"))
        self._dat_int = int(self._config.get("TRANSLATOR", "dat_int"))
        self._igr_int = int(self._config.get("TRANSLATOR", "igr_int"))
        self._ind_int = int(self._config.get("TRANSLATOR", "ind_int"))
        self._sou_int = int(self._config.get("TRANSLATOR", "sou_int"))

        #Creating objects that we will need during the parsing process
        self._datasets = []
        self._indicators_dict = self._build_indicators_dict()
        self._default_computation = self._build_default_computation()
        self._default_issued = self._build_default_issued()

        #Creating and managing common objects
        self._user = self._create_user()
        self._organization = self._create_organization()
        self._datasource = self._create_datasource()
        self._license = self._create_license()
        self._establish_relations_common_objects()


    def run(self):
        """
        Steps:
         - Turn file into an xml object in memory
         - Turn that object into model landportal objects
         - Turn model objects into a xml per dataset and send it to the receiver

        """
        available_table_trees = self._turn_file_tables_into_xml_objects()
        for tree in available_table_trees:
            self._datasets.append(self._create_dataset_from_table(tree))

        for dataset in self._datasets:
            self._decorate_dataset_with_common_objects(dataset)
            self._generate_xml_from_dataset_model(dataset)

    def _generate_xml_from_dataset_model(self, dataset):
        ModelToXMLTransformer(dataset=dataset,
                              import_process="xml",
                              user=self._user).run()


    @staticmethod
    def _create_user():
        user = User(user_login="UNDPImporter")
        user.ip = "156.35.X.X"  # CHANGE TODO
        user.timestamp = datetime.now()
        return user

    def _create_organization(self):
        organization = Organization(chain_for_id=self._org_id)
        organization.name = "UNDP: United Nations Development Programme"
        organization.url = "http://www.undp.org/"
        return organization

    def _create_datasource(self):
        datasource = DataSource(chain_for_id=self._org_id,
                                int_for_id=self._sou_int)
        self._sou_int += 1  # Updating ind id value for datasource
        datasource.name = "Human Development Index Data"
        return datasource

    def _create_license(self):
        obj_license = License()
        obj_license.name = "Free to use"  # TODO: Confirm with Carlos
        obj_license.description = "No use restrictions"
        obj_license.republish = True
        obj_license.url = "None!!"  # TODO : Confirm with Carlos
        return obj_license

    def _establish_relations_common_objects(self):
        self._organization.add_user(self._user)
        self._organization.add_data_source(self._datasource)


    def _decorate_dataset_with_common_objects(self, dataset):
        self._datasource.add_dataset(dataset)
        dataset.license_type = self._license  # The rest of the relations between with the objects that
        # we´ve just link to the dataset had already been stablished in
        #other methods

    @staticmethod
    def _build_default_issued():
        return Instant(instant=datetime.now())

    def _build_indicators_dict(self):
        result_dict = {}

        #Indicator hdi
        ind_hdi = Indicator(chain_for_id=self._org_id,
                            int_for_id=self._ind_int)
        self._ind_int += 1  # Updating indicator int id value
        ind_hdi.name = "HDI"
        ind_hdi.description = "Human Development Index. A tool developed by the United Nations to measure and \
                                rank countries' levels of social and economic development based on four criteria: \
                                Life expectancy at birth, mean years of schooling, expected years of schooling and \
                                gross national income per capita. The HDI makes it possible to track changes in \
                                development levels over time and to compare development levels in different countries."
        ind_hdi.measurement_unit = MeasurementUnit(name="%")
        result_dict[self.HDI_ENDING] = ind_hdi  # Adding to dictionary

        #Indicator rank
        ind_rank = Indicator(chain_for_id=self._org_id,
                             int_for_id=self._ind_int)
        self._ind_int += 1  # Updating indicator int id value
        ind_rank.name = "HDI rank"
        ind_rank.description = "Position in the world´s HDI ranking."
        ind_rank.measurement_unit = MeasurementUnit("rank")
        result_dict[self.RANK_ENDING] = ind_rank  # Adding to dictionary

        return result_dict

    @staticmethod
    def _build_default_computation():
        return Computation(uri=Computation.RAW)

    def _create_dataset_from_table(self, tree):
        dataset = self._create_empty_dataset()
        base_node = tree.getroot().find(self.BASE_ROW)
        for country_node in base_node.getchildren():
            self._add_country_info_to_dataset_from_country_node(dataset, country_node)
        return dataset

    def _add_country_info_to_dataset_from_country_node(self, dataset, country_node):
        valid_info_subnodes = self._filter_valid_info_subnodes(country_node)
        complete_observations = self._generate_complete_observations_from_valid_subnodes(valid_info_subnodes)
        for obs in complete_observations:
            dataset.add_observation(obs)
            #No return needed

    def _generate_complete_observations_from_valid_subnodes(self, subnodes):
        # Declaring needed temporal variables
        country_iso3 = ""
        country_name = ""
        no_country_obs = []

        # Detecting type of received nodes. Putting their info in the temporal variables.
        for node in subnodes:
            if node.tag == self.COUNTRY_CODE:
                country_iso3 = node.text
            elif node.tag == self.COUNTRY_NAME:
                country_name = node.text
            elif node.tag.endswith(self.HDI_ENDING):
                no_country_obs.append(self._build_hdi_obs_without_country(node))
            elif node.tag.endswith(self.RANK_ENDING):
                no_country_obs.append(self._build_rank_obs_without_country(node))
            else:
                raise RuntimeError('Trying to process an unexpected node: "{0}".'.format(node.tag))

        # Resolving country with the obtained data
        country_object = self._resolve_country(country_iso3=country_iso3, country_name=country_name)

        #Adding observations to country
        for obs in no_country_obs:
            country_object.add_observation(obs)

        #returnig every complete obs that we have built
        return no_country_obs  # They already have an associated country


    def _build_rank_obs_without_country(self, node):
        result = Observation(chain_for_id=self._org_id,
                             int_for_id=self._obs_int)

        self._obs_int += 1  # Updating obs_int id value
        result.value = self._build_observation_rank_value_object(node)
        result.indicator = self._get_observation_indicator_object(node)
        result.computation = self._get_observation_computation_object()  # Always the same, no param needed
        result.issued = self._get_observation_issued_object()  # Always the same, no param needed
        result.ref_time = self._build_observation_ref_time_object(node)
        return result

    def _build_hdi_obs_without_country(self, node):
        result = Observation(chain_for_id=self._org_id,
                             int_for_id=self._obs_int)

        self._obs_int += 1  # Updating obs_int id value

        result.value = self._build_observation_hdi_value_object(node)
        result.indicator = self._get_observation_indicator_object(node)
        result.computation = self._get_observation_computation_object()  # Always the same, no param needed
        result.issued = self._get_observation_issued_object()  # Always the same, no param needed
        result.ref_time = self._build_observation_ref_time_object(node)
        return result


    @staticmethod
    def _build_observation_ref_time_object(node):
        #Expected format of node_tag: _2010_hdi  or  _2010_hdi_rank
        #Both formats have single dtae,it is betwen "_" and at the beginning of the tag
        try:
            candidate_year = node.tag.split("_")[1]
            numeric_value = int(candidate_year)
            return YearInterval(year=str(numeric_value))
        except:
            raise RuntimeError("Unable to detect date in the next node {0}. Unexpected tag format".format(node.tag))


    def _get_observation_issued_object(self):
        return self._default_issued


    def _get_observation_computation_object(self):
        return self._default_computation


    @staticmethod
    def _build_observation_hdi_value_object(node):
        value = Value()
        value.obs_status = Value.AVAILABLE
        value.value_type = "float"
        value.value = float(node.text) * 100  # Turning a value between 0,1 into a percentage
        return value

    @staticmethod
    def _build_observation_rank_value_object(node):
        value = Value()
        value.obs_status = Value.AVAILABLE
        value.value_type = "int"
        value.value = int(node.text)
        return value


    def _get_observation_indicator_object(self, node):
        if node.tag.endswith(self.HDI_ENDING):
            return self._indicators_dict[self.HDI_ENDING]
        elif node.tag.endswith(self.RANK_ENDING):
            return self._indicators_dict[self.RANK_ENDING]
        else:
            raise RuntimeError("Unrecognized indicator while parsing the next node: '{0}'.".format(node.tag))


    def _resolve_country(self, country_iso3, country_name):
        try:
            return self._reconciler.get_country_by_iso3(country_iso3)
        except UnknownCountryError:
            try:
                return self._reconciler.get_country_by_en_name(country_name)
            except UnknownCountryError:
                raise RuntimeError('Unable to recognize country with the next info. Name: "{0}". ISO3: "{1}"' \
                                   .format(country_name, country_iso3))

    def _filter_valid_info_subnodes(self, country_node):
        result = []
        for subnode in country_node.getchildren():
            if not subnode.tag.startswith("_"):  # Country code and country name nodes
                result.append(subnode)
            elif subnode.tag.endswith(self.HDI_ENDING):  # Concrete hdi data by year
                result.append(subnode)
            elif subnode.tag.endswith(self.RANK_ENDING):  # HDI rank node
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
        base_directory = self._config.get("TRANSLATOR", "downloaded_data")
        candidate_files = os.listdir(base_directory)
        for candidate_file in candidate_files:
            if os.path.splitext(candidate_file)[1] == "xml":
                result.append(self._turn_table_file_into_xml_object(candidate_file))
        return result

    @staticmethod
    def _turn_table_file_into_xml_object(file_path):
        try:
            return ETree.parse(file_path)
        except:
            raise RuntimeError("Impossible to parse xml in path: {0}. \
                    It looks that it is not a valid xml file.".format(str(file_path)))


