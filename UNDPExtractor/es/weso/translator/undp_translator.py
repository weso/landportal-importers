# coding=utf-8
from es.weso.translator.pair_file_object import PairFileObject
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
import codecs
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

    def __init__(self, config, log, look_for_historical):
        self._config = config
        self._log = log
        self._reconciler = CountryReconciler()
        self._look_for_historical = look_for_historical

        #Getting propper ids
        self._org_id = self._config.get("TRANSLATOR", "org_id")
        if self._look_for_historical:
            self._obs_int = 0
            self._sli_int = 0
            self._dat_int = 0
            self._igr_int = 0
        else:
            self._obs_int = int(self._config.get("TRANSLATOR", "obs_int"))
            self._sli_int = int(self._config.get("TRANSLATOR", "sli_int"))
            self._dat_int = int(self._config.get("TRANSLATOR", "dat_int"))
            self._igr_int = int(self._config.get("TRANSLATOR", "igr_int"))

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
        available_table_trees_pairs = self._turn_file_tables_into_xml_objects()
        for pair in available_table_trees_pairs:
            dataset = self._create_dataset_from_table(pair.other_object)
            pair.other_object = dataset

        for pair in available_table_trees_pairs:
            self._decorate_dataset_with_common_objects(pair.other_object)

        for pair in available_table_trees_pairs:
            self._generate_xml_from_dataset_model(pair)

    def _generate_xml_from_dataset_model(self, pair):
        ModelToXMLTransformer(dataset=pair.other_object,
                              import_process=ModelToXMLTransformer.XML,
                              user=self._user,
                              path_to_original_file=pair.file_path).run()
        self._actualize_config_values()


    def _actualize_config_values(self):
        self._config.set("TRANSLATOR", "obs_int", self._obs_int)
        self._config.set("TRANSLATOR", "dat_int", self._dat_int)
        self._config.set("TRANSLATOR", "sli_int", self._sli_int)
        self._config.set("TRANSLATOR", "igr_int", self._igr_int)

        with open("./files/configuration.ini", 'wb') as config_file:
            self._config.write(config_file)

    def _create_user(self):
        user = User(user_login=self._config.get("USER", "login"))
        return user

    def _create_organization(self):
        organization = Organization(chain_for_id=self._org_id)
        organization.name = self._config.get("ORGANIZATION", "name")
        organization.url = self._config.get("ORGANIZATION", "url")
        organization.url_logo = self._config.get("ORGANIZATION", "url_logo")
        organization.description_en = self._read_config_value("ORGANIZATION", "description_en")
        organization.description_es = self._read_config_value("ORGANIZATION", "description_es")
        organization.description_fr = self._read_config_value("ORGANIZATION", "description_fr")
        return organization

    def _create_datasource(self):
        datasource = DataSource(chain_for_id=self._org_id,
                                int_for_id=self._config.get("DATASOURCE", "id"))
        datasource.name = self._config.get("DATASOURCE", "name")
        return datasource

    def _create_license(self):
        obj_license = License()
        obj_license.name = self._config.get("LICENSE", "name")
        obj_license.description = self._config.get("LICENSE", "description")
        obj_license.republish = self._config.get("LICENSE", "republish")
        obj_license.url = self._config.get("LICENSE", "url")
        return obj_license

    def _establish_relations_common_objects(self):
        self._organization.add_user(self._user)
        self._organization.add_data_source(self._datasource)


    def _decorate_dataset_with_common_objects(self, dataset):
        self._datasource.add_dataset(dataset)
        dataset.license_type = self._license  # The rest of the relations between with the objects that
        # we've just link to the dataset had already been established in other methods


    @staticmethod
    def _build_default_issued():
        return Instant(instant=datetime.now())

    def _build_indicators_dict(self):
        result_dict = {}

        #Indicator hdi
        ind_hdi = Indicator(chain_for_id=self._org_id,
                            int_for_id=self._config.get("IND_DESCRIPTION", "hdi_id"))
        ind_hdi.name_en = self._read_config_value("IND_DESCRIPTION", "hdi_name_en")  # Done
        ind_hdi.name_es = self._read_config_value("IND_DESCRIPTION", "hdi_name_es")  # Done
        ind_hdi.name_fr = self._read_config_value("IND_DESCRIPTION", "hdi_name_fr")  # Done
        ind_hdi.description_en = self._read_config_value("IND_DESCRIPTION", "hdi_desc_en")  # Done
        ind_hdi.description_es = self._read_config_value("IND_DESCRIPTION", "hdi_desc_es")  # Done
        ind_hdi.description_fr = self._read_config_value("IND_DESCRIPTION", "hdi_desc_fr")  # Done
        ind_hdi.measurement_unit = MeasurementUnit(name="HDI value",
                                                   convert_to=MeasurementUnit.INDEX)
        ind_hdi.preferable_tendency = Indicator.INCREASE
        ind_hdi.topic = self._config.get("IND_DESCRIPTION", "hdi_topic")

        result_dict[self.HDI_ENDING] = ind_hdi  # Adding to dictionary

        #Indicator rank
        ind_rank = Indicator(chain_for_id=self._org_id,
                             int_for_id=self._config.get("IND_DESCRIPTION", "hdi_rank_id"))
        ind_rank.name_en = self._read_config_value("IND_DESCRIPTION", "hdi_rank_name_en")  # Done
        ind_rank.name_es = self._read_config_value("IND_DESCRIPTION", "hdi_rank_name_es")  # Done
        ind_rank.name_fr = self._read_config_value("IND_DESCRIPTION", "hdi_rank_name_fr")  # Done

        ind_rank.description_en = self._read_config_value("IND_DESCRIPTION", "hdi_rank_desc_en")   # Done
        ind_rank.description_es = self._read_config_value("IND_DESCRIPTION", "hdi_rank_desc_es")  # Done
        ind_rank.description_fr = self._read_config_value("IND_DESCRIPTION", "hdi_rank_desc_fr")  # Done
        ind_rank.measurement_unit = MeasurementUnit(name="Ranking",
                                                    convert_to=MeasurementUnit.RANK)
        ind_rank.preferable_tendency = Indicator.DECREASE

        ind_rank.topic = self._config.get("IND_DESCRIPTION", "hdi_rank_topic")

        result_dict[self.RANK_ENDING] = ind_rank  # Adding to dictionary

        return result_dict


    def _read_config_value(self, section, field):
        return (self._config.get(section, field)).decode(encoding="utf-8")

    @staticmethod
    def _build_default_computation():
        return Computation(uri=Computation.RAW)

    def _create_dataset_from_table(self, tree):
        dataset = self._create_empty_dataset()
        base_node = tree.find(self.BASE_ROW)
        for country_node in base_node.getchildren():
            self._add_country_info_to_dataset_from_country_node(dataset, country_node)
        return dataset

    def _add_country_info_to_dataset_from_country_node(self, dataset, country_node):
        valid_info_subnodes = self._filter_valid_info_subnodes(country_node)
        try:
            complete_observations = self._generate_complete_observations_from_valid_subnodes(valid_info_subnodes)
            for obs in complete_observations:
                dataset.add_observation(obs)
                #No return needed
        except UnknownCountryError as e:
            self._log.info("Ignoring row node. Cause: {0}". format(e))

    def _generate_complete_observations_from_valid_subnodes(self, subnodes):
        # Declaring needed temporal variables
        country_iso3 = ""
        country_name = ""
        no_country_observations = []

        # Detecting type of received nodes. Putting their info in the temporal variables.
        for node in subnodes:
            if node.tag == self.COUNTRY_CODE:
                country_iso3 = self._node_text(node)
            elif node.tag == self.COUNTRY_NAME:
                country_name = self._node_text(node)
            elif node.tag.endswith(self.HDI_ENDING):
                no_country_observations.append(self._build_hdi_obs_without_country(node))
            elif node.tag.endswith(self.RANK_ENDING):
                no_country_observations.append(self._build_rank_obs_without_country(node))
            else:
                raise RuntimeError('Trying to process an unexpected node: "{0}".'.format(node.tag))

        # Resolving country with the obtained data
        country_object = self._resolve_country(country_iso3=country_iso3, country_name=country_name)

        result = []  # Will contain the valid final obs
        #Adding observations to country and passing filters
        for obs in no_country_observations:
            if self._pass_filters(obs):
                country_object.add_observation(obs)
                result.append(obs)


        #returnig every complete obs that we have built
        return result  # They already have an associated country

    def _pass_filters(self, obs):
        if self._look_for_historical:
            return True
        if not "_target_date" in self.__dict__:
            self._target_date = self._get_current_date()
        elif self._get_year_of_observation(obs) < self._target_date:
            return False
        return True


    def _get_current_date(self):
        return int(self._config.get("HISTORICAL", "first_valid_year"))


    @staticmethod
    def _get_year_of_observation(obs):
        date_obj = obs.ref_time
        if type(date_obj) == YearInterval:
            return int(date_obj.year)
        else:
            raise RuntimeError("Unexpected object date. Impossible to build observation from it: " + type(date_obj))


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


    def _build_observation_hdi_value_object(self, node):
        value = Value()
        value.obs_status = Value.AVAILABLE
        value.value_type = "float"
        value.value = float(self._node_text(node))
        return value

    def _build_observation_rank_value_object(self, node):
        value = Value()
        value.obs_status = Value.AVAILABLE
        value.value_type = "int"
        value.value = int(self._node_text(node))
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
            result = self._reconciler.get_country_by_iso3(country_iso3)
            if "Ivoire" in result.name:
                raise UnknownCountryError("")
            return result
        except UnknownCountryError:
            try:
                result = self._reconciler.get_country_by_en_name(country_name)
                if "Ivoire" in result.name:
                    raise UnknownCountryError("")
                return result
            except UnknownCountryError:
                raise UnknownCountryError('Unable to recognize country with the next info. Name: "{0}". ISO3: "{1}"' \
                                   .format(country_name, country_iso3))  # we are just changing the error message

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
            if os.path.splitext(candidate_file)[1] == ".xml":
                result.append(
                    PairFileObject(os.path.abspath(os.path.join(base_directory, candidate_file)),
                                   self._turn_table_file_into_xml_object(base_directory + "/" + candidate_file)))
        return result

    @staticmethod
    def _turn_table_file_into_xml_object(file_path):
        try:
            content_file = codecs.open(file_path, encoding='utf-8')
            lines = content_file.readlines()
            content_file.close()
            return ETree.fromstring(lines[0].encode(encoding="utf-8"))

        except BaseException:
            raise RuntimeError("Impossible to parse xml in path: {0}. \
                    It looks that it is not a valid xml file.".format(str(file_path)))

    @staticmethod
    def _node_text(node):
        return node.text.encode(encoding="utf-8")
