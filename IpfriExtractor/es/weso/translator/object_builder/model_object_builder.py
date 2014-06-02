# coding=utf-8
__author__ = 'Dani'

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
from lpentities.slice import Slice

from reconciler.country_reconciler import CountryReconciler
from reconciler.exceptions.unknown_country_error import UnknownCountryError

from .dates_builder import get_model_object_time_from_parsed_string
from ..dataset_user_pair import DatasetUserFileGroup

from datetime import datetime


class IpfriModelObjectBuilder(object):
    def __init__(self, log, config, parsed_indicators, parsed_dates, parsed_countries, file_path):

        self._log = log
        self._config = config
        self._parsed_indicators = parsed_indicators
        self._parsed_dates = parsed_dates
        self._parsed_countries = parsed_countries
        self._file_path = file_path

        self._indicators_dict = {}
        self._dates_dict = {}
        self._countries_dict = {}

        #Initializing variable ids
        self._org_id = self._config.get("TRANSLATOR", "org_id")
        self._obs_int = int(self._config.get("TRANSLATOR", "obs_int", True))
        self._sli_int = int(self._config.get("TRANSLATOR", "sli_int", True))
        self._dat_int = int(self._config.get("TRANSLATOR", "dat_int", True))
        self._igr_int = int(self._config.get("TRANSLATOR", "igr_int", True))

        self.dataset = None
        self.user = None
        self.reconciler = CountryReconciler()


    def run(self):
        self.prepare_base_hierarchy_objects()
        self.complete_indicators_dict()
        self.complete_dates_dict()
        self.complete_countries_dict()
        self.fetch_elements_by_index_and_translate()
        self._put_self_id_values_in_the_config_file()
        return DatasetUserFileGroup(self.dataset, self.user, self._file_path)


    def _put_self_id_values_in_the_config_file(self):
        self._config.set("TRANSLATOR", "obs_int", self._obs_int)
        self._config.set("TRANSLATOR", "sli_int", self._sli_int)
        self._config.set("TRANSLATOR", "dat_int", self._dat_int)
        self._config.set("TRANSLATOR", "igr_int", self._igr_int)


    def prepare_base_hierarchy_objects(self):
        #Building dataset
        self.dataset = Dataset(chain_for_id=self._org_id, int_for_id=self._dat_int)
        self._dat_int += 1  # Updating int_id value
        self.dataset.frequency = Dataset.YEARLY

        #Building license
        new_license = License()
        new_license.name = self._config.get("LICENSE", "name")  #
        new_license.description = self._config.get("LICENSE", "description")  #
        new_license.republish = self._config.get("LICENSE", "republish")  #
        new_license.url = self._config.get("LICENSE", "url")  #

        self.dataset.license_type = new_license

        #building datasource
        new_datasource = DataSource(chain_for_id=self._org_id,
                                    int_for_id=self._config.get("DATASOURCE", "id"))
        new_datasource.name = self._config.get("DATASOURCE", "name")

        new_datasource.add_dataset(self.dataset)

        # Building organization
        new_organization = Organization(chain_for_id=self._org_id)
        new_organization.name = self._read_config_value("ORGANIZATION", "name")
        new_organization.url = self._read_config_value("ORGANIZATION", "url")
        new_organization.description_en = self._read_config_value("ORGANIZATION", "description_en")
        new_organization.description_es = self._read_config_value("ORGANIZATION", "description_es")
        new_organization.description_fr = self._read_config_value("ORGANIZATION", "description_fr")
        # new_organization.url_logo = self._read_config_value("ORGANIZATION", "url_logo")

        new_organization.add_data_source(new_datasource)

        #Building user
        self.user = User(user_login=self._config.get("USER", "login"))
        new_organization.add_user(self.user)


    def _read_config_value(self, section, field):
        return (self._config.get(section, field)).decode(encoding="utf-8")


    def complete_countries_dict(self):
        for pcountry in self._parsed_countries:
            try:
                new_country = self.reconciler.get_country_by_en_name(pcountry.name)
            except UnknownCountryError:
                self._log.warning("Unrecognized country: {0}. Its observations will be ignored".format(pcountry.name))
                new_country = None
            self._countries_dict[pcountry.name] = new_country

    def complete_dates_dict(self):
        for pdate in self._parsed_dates:
            time_object = get_model_object_time_from_parsed_string(pdate.string_date)
            self._dates_dict[pdate.string_date] = time_object


    def complete_indicators_dict(self):
        """
        In order to unify thge possible variant names that comes form the excell, in this point
        we are going to change the pindicator.name of every pindicator object
        """
        for pindicator in self._parsed_indicators:
            if "undernourishment" in pindicator.name or "undernourished" in pindicator.name:
                pindicator.name = "undernourishment"
                self._add_indicator_to_dict_if_needed(pindicator.name, "undernourishment")
            elif "underweight" in pindicator.name:
                pindicator.name = "underweight"
                self._add_indicator_to_dict_if_needed(pindicator.name, "underweight")
            elif "Mortality" in pindicator.name or "mortality" in pindicator.name:
                pindicator.name = "mortality"
                self._add_indicator_to_dict_if_needed(pindicator.name, "mortality")
            elif "GHI" in pindicator.name or "Hunger Index" in pindicator.name:
                pindicator.name = "GHI"
                self._add_indicator_to_dict_if_needed(pindicator.name, "ghi")
            else:
                raise RuntimeError("Unrecognized indicator: {0}".format(pindicator.name))

    def _add_indicator_to_dict_if_needed(self, key, begin_of_the_pattern):
        if key in self._indicators_dict:
            return
        else:
            new_indicator = Indicator(chain_for_id=self._org_id,
                                      int_for_id=self._config.get("INDICATOR", begin_of_the_pattern + "_id"))
            new_indicator.name_en = self._read_config_value("INDICATOR", begin_of_the_pattern + "_name_en")
            new_indicator.name_es = self._read_config_value("INDICATOR", begin_of_the_pattern + "_name_es")
            new_indicator.name_fr = self._read_config_value("INDICATOR", begin_of_the_pattern + "_name_fr")
            new_indicator.description_en = self._read_config_value("INDICATOR", begin_of_the_pattern + "_desc_en")
            new_indicator.description_es = self._read_config_value("INDICATOR", begin_of_the_pattern + "_desc_es")
            new_indicator.description_fr = self._read_config_value("INDICATOR", begin_of_the_pattern + "_desc_fr")
            new_indicator.measurement_unit = MeasurementUnit(name="%",
                                                             convert_to=MeasurementUnit.PERCENTAGE)

            new_indicator.preferable_tendency = Indicator.DECREASE
            new_indicator.topic = self._config.get("INDICATOR", begin_of_the_pattern + "_topic")

            self._indicators_dict[key] = new_indicator
            #Completing dataset object
            self.dataset.add_indicator(new_indicator)


    def fetch_elements_by_index_and_translate(self):
        sliceid = 0
        for pdate in self._parsed_dates:
            pindicator = self.find_pindicator_by_pdate(pdate)
            sliceid += 1
            new_slice = self._generate_slice_by_pdate_and_pindicator(pdate, pindicator, sliceid)
            for pcountry in self._parsed_countries:
                new_obs = self.generate_observation_with_model_objects(pindicator, pdate, pcountry)
                new_slice.add_observation(new_obs)
                self.dataset.add_observation(new_obs)

            self.dataset.add_slice(new_slice)

    def _generate_slice_by_pdate_and_pindicator(self, pdate, pindicator, sliceid):
        result = Slice(chain_for_id=self._org_id, int_for_id=self._sli_int)
        self._sli_int += 1  # Updating int id value
        result.indicator = self._indicators_dict[pindicator.name]
        result.dimension = self._dates_dict[pdate.string_date]

        return result

    def generate_observation_with_model_objects(self, pindicator, pdate, pcountry):
        #Building obs
        excell_value = self.look_for_value_in_a_pdate(pdate, pcountry)
        new_obs = Observation(chain_for_id=self._org_id, int_for_id=self._obs_int)
        self._obs_int += 1  # Update int id value
        self.add_value_object_to_observation(excell_value, new_obs)
        self.add_indicator_object_to_observation(pindicator, new_obs)
        self.add_computation_object_to_observation(excell_value, new_obs)
        self.add_issued_object_to_observation(new_obs)
        self.add_ref_time_object_to_observation(pdate, new_obs)
        self.add_country_object_to_observation(pcountry, new_obs)

        #Returning obs
        return new_obs

    def add_country_object_to_observation(self, pcountry, new_obs):
        country_object = self._countries_dict[pcountry.name]
        country_object.add_observation(new_obs)
        #No return needed. Modyfing new_obs object

    def add_ref_time_object_to_observation(self, pdate, new_obs):
        new_obs.ref_time = self._dates_dict[pdate.string_date]
        #No return. Modifying received new_obs

    def add_issued_object_to_observation(self, new_obs):
        new_issued = Instant(datetime.now())
        new_obs.issued = new_issued
        #No return. Modifying received new_obs

    def add_computation_object_to_observation(self, excell_value, new_obs):
        if excell_value is None or not excell_value.estimated:
            if not self.__dict__.has_key("default_raw"):
                self.default_raw = Computation(uri=Computation.RAW)
            new_obs.computation = self.default_raw
        else:
            if not self.__dict__.has_key("default_estimated"):
                self.default_estimated = Computation(uri=Computation.ESTIMATED)
            new_obs.computation = self.default_estimated

            # No returning sentence needed

    def add_indicator_object_to_observation(self, pindicator, new_obs):
        new_obs.indicator = self._indicators_dict[pindicator.name]

    def add_value_object_to_observation(self, excell_value, new_obs):
        obs_value = Value()

        if excell_value is None:
            obs_value.value = None
            obs_value.obs_status = Value.MISSING
            obs_value.value_type = "float"
        else:
            obs_value.value = excell_value.value
            obs_value.obs_status = Value.AVAILABLE
            obs_value.value_type = "float"

        new_obs.value = obs_value
        # No return sentence needed. Modifying received new_obs object

    def look_for_value_in_a_pdate(self, pdate, pcountry):
        """
        If the value exist, it returns it. Elsewhere, it returns None

        """
        for a_value in pcountry.values:
            if pdate.beg_col <= a_value.column <= pdate.end_col:
                return a_value
        return None  # We reach this sentence only if the loop ends without executing the if´s body

    def find_pindicator_by_pdate(self, pdate):
        for pindicator in self._parsed_indicators:
            if pdate.beg_col >= pindicator.beg_col and pdate.end_col <= pindicator.end_col:
                return pindicator
        raise RuntimeError("Unable to find indicator to the date {0}".format(pdate.string_date))
