from es.weso.faogenderextractor.extractor.keys_dict import KeysDict

__author__ = 'Dani'


from datetime import datetime

from model2xml.model2xml import ModelToXMLTransformer

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


class ModelObjectBuilder(object):

    def __init__(self, log, config, registers):
        self._log = log
        self._config = config
        self._registers = registers

        #Initializing variable ids
        self._org_id = self._config.get("TRANSLATOR", "org_id")
        self._obs_int = int(self._config.get("TRANSLATOR", "obs_int"))
        self._sli_int = int(self._config.get("TRANSLATOR", "sli_int"))
        self._dat_int = int(self._config.get("TRANSLATOR", "dat_int"))
        self._igr_int = int(self._config.get("TRANSLATOR", "igr_int"))
        self._ind_int = int(self._config.get("TRANSLATOR", "ind_int"))
        self._sou_int = int(self._config.get("TRANSLATOR", "sou_int"))


        self._indicators_dict = self._build_indicators_dict()

        #Building common objects
        self._default_user = self._build_default_user()  # Done
        self._default_datasource = self._build_default_datasource()  # TODO
        self._default_dataset = self._build_default_dataset()  # TODO
        self._default_organization = self._build_default_organization()  # TODO
        self._default_license = self._build_default_license()  # TODO
        self._relate_common_objects()  # TODO

        self._default_computation = Computation(uri=Computation.RAW)

    def run(self):
        observations = []
        for a_register in self._registers:
            observations += self._build_observations_from_register(a_register)

        for obs in observations:
            self._default_dataset.add_observation(obs)

        ModelToXMLTransformer(dataset=self._default_dataset, import_process="API Rest", user=self._default_user).run()



    def _build_observations_from_register(self, register):
        result = []
        for indicator_data in register.get_available_data():  # list of IndicatorData objects
            result.append(self._build_observation_from_an_indicator_data_object(indicator_data, register.country))
        return result

    def _build_observation_from_an_indicator_data_object(self, indicator_data, country):
        result = Observation(chain_for_id=self._org_id,
                             int_for_id=self._obs_int)
        self._obs_int += 1  # Updating int id value

        #Indicator
        result.indicator = self._get_indicator_object_from_indicator_data(indicator_data)
        #Value
        result.value = self._build_value_object_from_indicator_data(indicator_data)
        #Computation
        result.computation = self._default_computation
        #Issued
        result.issued = self._build_issued_object()  # No param needed
        #Ref-time
        result.ref_time = self._get_ref_time_object_from_indicator_data(indicator_data)
        #Region
        country.add_observation(result)  # And that stablish teh relationship in both directions, and make countries
                                        #countries reachable through navigation from dataset

        return result


    @staticmethod
    def _get_ref_time_object_from_indicator_data(indicator_data):
        if indicator_data.date is None:
            raise RuntimeError("Observation without associated date. value {0}, indicator code {1}"
                               .format(indicator_data.value, indicator_data.indicator_code))
        else:
            return indicator_data.date

    @staticmethod
    def _build_issued_object():
        return Instant(instant=datetime.now())


    def _get_indicator_object_from_indicator_data(self, indicator_data):
        return self._indicators_dict[indicator_data.indicator_code]


    @staticmethod
    def _build_value_object_from_indicator_data(indicator_data):
        if indicator_data.value is None:
            return Value(value=None,
                         obs_status=Value.MISSING,
                         value_type=Value.INTEGER)
        else:
            return Value(value=indicator_data.value,
                         obs_status=Value.AVAILABLE,
                         value_type=Value.INTEGER)


    def _build_default_user(self):
        return User(user_login=self._config.get("USER", "login"))

    def _build_default_datasource(self):
        result = DataSource(chain_for_id=self._org_id,
                            int_for_id=self._sou_int)
        self._sou_int += 1  # Updating int id value
        result.name = self._config.get("DATASOURCE", "name")
        return result

    def _build_default_dataset(self):
        result = Dataset(chain_for_id=self._org_id, int_for_id=self._dat_int)
        self._dat_int += 1  # Needed increment
        result.frequency = Dataset.YEARLY  # TODO. No idea!
        return result

    def _build_default_organization(self):
        result = Organization(chain_for_id=self._org_id)
        result.name = self._config.get("ORGANIZATION", "name")
        result.url = self._config.get("ORGANIZATION", "url")
        result.url_logo = self._config.get("ORGANIZATION", "url_logo")
        result.description = self._config.get("ORGANIZATION", "description")

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
        
        #rural_household_women
        rural_households_women_ind = Indicator(chain_for_id=self._org_id, int_for_id=self._ind_int)
        self._ind_int += 1
        rural_households_women_ind.name_en = self._read_config_value("INDICATOR", "rural_households_women_name_en")
        rural_households_women_ind.name_es = self._read_config_value("INDICATOR", "rural_households_women_name_es")
        rural_households_women_ind.name_fr = self._read_config_value("INDICATOR", "rural_households_women_name_fr")
        rural_households_women_ind.description_en = self._read_config_value("INDICATOR", "rural_households_women_desc_en")
        rural_households_women_ind.description_es = self._read_config_value("INDICATOR", "rural_households_women_desc_es")
        rural_households_women_ind.description_fr = self._read_config_value("INDICATOR", "rural_households_women_desc_fr")
        rural_households_women_ind.measurement_unit = MeasurementUnit("units")
        rural_households_women_ind.topic = Indicator.TOPIC_TEMPORAL
        rural_households_women_ind.preferable_tendency = Indicator.INCREASE
        
        result[KeysDict.RURAL_HOUSEHOLDS_WOMEN_CODE] = rural_households_women_ind
        
        #holdings_co_ownership
        holdings_co_ownership_ind = Indicator(chain_for_id=self._org_id, int_for_id=self._ind_int)
        self._ind_int += 1
        holdings_co_ownership_ind.name_en = self._read_config_value("INDICATOR", "holdings_co_ownership_name_en")
        holdings_co_ownership_ind.name_es = self._read_config_value("INDICATOR", "holdings_co_ownership_name_es")
        holdings_co_ownership_ind.name_fr = self._read_config_value("INDICATOR", "holdings_co_ownership_name_fr")
        holdings_co_ownership_ind.description_en = self._read_config_value("INDICATOR", "holdings_co_ownership_desc_en")
        holdings_co_ownership_ind.description_es = self._read_config_value("INDICATOR", "holdings_co_ownership_desc_es")
        holdings_co_ownership_ind.description_fr = self._read_config_value("INDICATOR", "holdings_co_ownership_desc_fr")
        holdings_co_ownership_ind.measurement_unit = MeasurementUnit("units")
        holdings_co_ownership_ind.topic = Indicator.TOPIC_TEMPORAL
        holdings_co_ownership_ind.preferable_tendency = Indicator.INCREASE
        
        result[KeysDict.HOLDINGS_CO_OWNERSHIP_CODE] = holdings_co_ownership_ind
        
        #women_holders
        women_holders_ind = Indicator(chain_for_id=self._org_id, int_for_id=self._ind_int)
        self._ind_int += 1
        women_holders_ind.name_en = self._read_config_value("INDICATOR", "women_holders_name_en")
        women_holders_ind.name_es = self._read_config_value("INDICATOR", "women_holders_name_es")
        women_holders_ind.name_fr = self._read_config_value("INDICATOR", "women_holders_name_fr")
        women_holders_ind.description_en = self._read_config_value("INDICATOR", "women_holders_desc_en")
        women_holders_ind.description_es = self._read_config_value("INDICATOR", "women_holders_desc_es")
        women_holders_ind.description_fr = self._read_config_value("INDICATOR", "women_holders_desc_fr")
        women_holders_ind.measurement_unit = MeasurementUnit("units")
        women_holders_ind.topic = Indicator.TOPIC_TEMPORAL
        women_holders_ind.preferable_tendency = Indicator.INCREASE
        
        result[KeysDict.WOMEN_HOLDERS_CODE] = women_holders_ind
        
        #total_holders
        total_holders_ind = Indicator(chain_for_id=self._org_id, int_for_id=self._ind_int)
        self._ind_int += 1
        total_holders_ind.name_en = self._read_config_value("INDICATOR", "total_holders_name_en")
        total_holders_ind.name_es = self._read_config_value("INDICATOR", "total_holders_name_es")
        total_holders_ind.name_fr = self._read_config_value("INDICATOR", "total_holders_name_fr")
        total_holders_ind.description_en = self._read_config_value("INDICATOR", "total_holders_desc_en")
        total_holders_ind.description_es = self._read_config_value("INDICATOR", "total_holders_desc_es")
        total_holders_ind.description_fr = self._read_config_value("INDICATOR", "total_holders_desc_fr")
        total_holders_ind.measurement_unit = MeasurementUnit("units")
        total_holders_ind.topic = Indicator.TOPIC_TEMPORAL
        total_holders_ind.preferable_tendency = Indicator.INCREASE
        
        result[KeysDict.TOTAL_HOLDERS_CODE] = total_holders_ind

        return result


    def _read_config_value(self, section, field):
        return (self._config.get(section, field)).decode(encoding="utf-8")