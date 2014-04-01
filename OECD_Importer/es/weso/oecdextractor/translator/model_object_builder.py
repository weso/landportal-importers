from reconciler.exceptions.unknown_country_error import UnknownCountryError

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
from lpentities.year_interval import YearInterval

from reconciler.country_reconciler import CountryReconciler

from datetime import datetime


class ModelObjectBuilder(object):

    INDICATOR_JSON = "VARIABLE"
    ISO3_JSON = "LOCATION"
    VALUE_JSON = "Value"
    YEAR_JSON = "YEAR"




    def __init__(self, log, config, json_objects):
        self._log = log
        self._config = config
        self._json_objects = json_objects


        # Getting propper ids
        self._org_id = self._config.get("TRANSLATOR", "org_id")
        self._obs_int = int(self._config.get("TRANSLATOR", "obs_int"))
        self._sli_int = int(self._config.get("TRANSLATOR", "sli_int"))
        self._dat_int = int(self._config.get("TRANSLATOR", "dat_int"))
        self._igr_int = int(self._config.get("TRANSLATOR", "igr_int"))
        self._ind_int = int(self._config.get("TRANSLATOR", "ind_int"))
        self._sou_int = int(self._config.get("TRANSLATOR", "sou_int"))

        # Creating objects that would be necessary during the construction of the model
        self._indicators_dict = self._build_indicators_dict()
        self._default_computation = self._build_default_computation()
        self._countries_dict = {}  # It will be completed during the parsing process
        self._reconciler = CountryReconciler
        self._default_user = self._build_default_user()
        self._default_organization = self._build_default_organization()
        self._default_datasource = self._build_default_datasource()
        self._default_license = self._build_default_license()
        self.relate_common_objects()



    def _build_default_license(self):
        result = License()
        result.description = self._config.get("LICENSE", "license_desc")
        result.name = self._config.get("LICENSE", "license_name")
        result.republish = bool(self._config.get("LICENSE", "license_republish"))
        result.url = self._config.get("LICENSE", "license_url")
        return result

    def _build_default_organization(self):
        result = Organization(chain_for_id=self._org_id)
        result.name = self._config.get("ORGANIZATION", "oecd_name")
        result.url = self._config.get("ORGANIZATION", "oecd_url")
        result.description = self._config.get("ORGANIZATION", "oecd_desc")
        return result

    def _build_default_datasource(self):
        result = DataSource(chain_for_id=self._org_id, int_for_id=self._dat_int)
        self._dat_int += 1  # Updating int id dataset value
        return result

    def _build_default_user(self):
        result = User(user_login=self._config.get("USER", "user_name"))
        return result

    def relate_common_objects(self):
        """
        Most of the default obejects need to be related, and that relationship should be established only once.
        This method should be invoked from the constructor.

        """
        self._default_organization.add_user(self._default_user)
        self._default_organization.add_data_source(self._default_datasource)

    def run(self):
        """
        This method should return a list of dataset objects

        """
        result = []
        for a_json in self._json_objects:
            result.append(self._turn_json_into_dataset_object(a_json))
        return result

    @staticmethod
    def _build_default_computation():
        return Computation(Computation.RAW)

    def _build_indicators_dict(self):
        result = {}

        #Prepearing measurement units
        index_unit = MeasurementUnit(name="1 to 1 index")
        rank_unit = MeasurementUnit(name="rank")


        #SIGI
        sigi_ind = Indicator(chain_for_id=self._org_id, int_for_id=self._ind_int)
        self._ind_int += 1  # Updating ind id int value
        sigi_ind.name_en = self._config.get("INDICATORS", "sigi_name_en")  # TODO:
        sigi_ind.name_es = self._config.get("INDICATORS", "sigi_name_es")  # TODO:
        sigi_ind.name_fr = self._config.get("INDICATORS", "sigi_name_fr")  # TODO: translation is possibly available
        sigi_ind.description_en = self._config.get("INDICATORS", "sigi_desc_en")  # TODO:
        sigi_ind.description_es = self._config.get("INDICATORS", "sigi_desc_es")  # TODO:
        sigi_ind.description_fr = self._config.get("INDICATORS", "sigi_desc_fr")  # TODO: translation is possibly av.
        sigi_ind.topic = Indicator.TOPIC_TEMPORAL
        sigi_ind.measurement_unit = index_unit
        result[self._config.get("INDICATORS", "sigi_key")] = sigi_ind

        #SIGI RANK
        sigi_rank_ind = Indicator(chain_for_id=self._org_id, int_for_id=self._ind_int)
        self._ind_int += 1  # Updating ind id int value
        sigi_rank_ind.name_en = self._config.get("INDICATORS", "sigi_rank_name_en")  # TODO:
        sigi_rank_ind.name_es = self._config.get("INDICATORS", "sigi_rank_name_es")  # TODO:
        sigi_rank_ind.name_fr = self._config.get("INDICATORS", "sigi_rank_name_fr")  # TODO: translation is possibly av.
        sigi_rank_ind.description_en = self._config.get("INDICATORS", "sigi_rank_desc_en")  # TODO:
        sigi_rank_ind.description_es = self._config.get("INDICATORS", "sigi_rank_desc_es")  # TODO:
        sigi_rank_ind.description_fr = self._config.get("INDICATORS", "sigi_rank_desc_fr")  # TODO: tr possibly av.
        sigi_rank_ind.topic = Indicator.TOPIC_TEMPORAL
        sigi_rank_ind.measurement_unit = rank_unit
        result[self._config.get("INDICATORS", "sigi_rank_key")] = sigi_rank_ind


        #FC
        fc_ind = Indicator(chain_for_id=self._org_id, int_for_id=self._ind_int)
        self._ind_int += 1  # Updating ind id int value
        fc_ind.name_en = self._config.get("INDICATORS", "fc_name_en")  # TODO:
        fc_ind.name_es = self._config.get("INDICATORS", "fc_name_es")  # TODO:
        fc_ind.name_fr = self._config.get("INDICATORS", "fc_name_fr")  # TODO: translation is possibly av.
        fc_ind.description_en = self._config.get("INDICATORS", "fc_rank_name_en")  # TODO:
        fc_ind.description_es = self._config.get("INDICATORS", "fc_rank_name_es")  # TODO:
        fc_ind.description_fr = self._config.get("INDICATORS", "fc_rank_name_fr")  # TODO: translation is possibly av.
        fc_ind.topic = Indicator.TOPIC_TEMPORAL
        fc_ind.measurement_unit = index_unit
        result[self._config.get("INDICATORS", "fc_key")] = fc_ind

        #FC RANK
        fc_rank_ind = Indicator(chain_for_id=self._org_id, int_for_id=self._ind_int)
        self._ind_int += 1  # Updating ind id int value
        fc_rank_ind.name_en = self._config.get("INDICATORS", "fc_rank_name_en")  # TODO:
        fc_rank_ind.name_es = self._config.get("INDICATORS", "fc_rank_name_es")  # TODO:
        fc_rank_ind.name_fr = self._config.get("INDICATORS", "fc_rank_name_fr")  # TODO: translation is possibly av.
        fc_rank_ind.description_en = self._config.get("INDICATORS", "fc_rank_name_en")  # TODO:
        fc_rank_ind.description_es = self._config.get("INDICATORS", "fc_rank_name_es")  # TODO:
        fc_rank_ind.description_fr = self._config.get("INDICATORS", "fc_rank_name_fr")  # TODO: tr. possibly av.
        fc_rank_ind.topic = Indicator.TOPIC_TEMPORAL
        fc_rank_ind.measurement_unit = rank_unit
        result[self._config.get("INDICATORS", "fc_rank_key")] = fc_rank_ind

        #CIVIL
        civil_ind = Indicator(chain_for_id=self._org_id, int_for_id=self._ind_int)
        self._ind_int += 1  # Updating ind id int value
        civil_ind.name_en = self._config.get("INDICATORS", "civil_name_en")  # TODO:
        civil_ind.name_es = self._config.get("INDICATORS", "civil_name_es")  # TODO :
        civil_ind.name_fr = self._config.get("INDICATORS", "civil_name_fr")  # TODO: translation is possibly av.
        civil_ind.description_en = self._config.get("INDICATORS", "civil_rank_name_en")  # TODO:
        civil_ind.description_es = self._config.get("INDICATORS", "civil_rank_name_es")  # TODO:
        civil_ind.description_fr = self._config.get("INDICATORS", "civil_rank_name_fr")  # TODO: TR. POSSIBLY AV.
        civil_ind.topic = Indicator.TOPIC_TEMPORAL
        civil_ind.measurement_unit = index_unit
        result[self._config.get("INDICATORS", "civil_key")] = civil_ind

        #CIVIL RANK
        civil_rank_ind = Indicator(chain_for_id=self._org_id, int_for_id=self._ind_int)
        self._ind_int += 1  # Updating ind id int value
        civil_rank_ind.name_en = self._config.get("INDICATORS", "civil_rank_name_en")  # TODO:
        civil_rank_ind.name_es = self._config.get("INDICATORS", "civil_rank_name_es")  # TODO:
        civil_rank_ind.name_fr = self._config.get("INDICATORS", "civil_rank_name_fr")  # TODO: tr. possibly av.
        civil_rank_ind.description_en = self._config.get("INDICATORS", "civil_rank_name_en")  # TODO:
        civil_rank_ind.description_es = self._config.get("INDICATORS", "civil_rank_name_es")  # TODO:
        civil_rank_ind.description_fr = self._config.get("INDICATORS", "civil_rank_name_fr")  # TODO: tr. possibly av.
        civil_rank_ind.measurement_unit = rank_unit
        civil_rank_ind.topic = Indicator.TOPIC_TEMPORAL
        result[self._config.get("INDICATORS", "civil_rank_key")] = civil_rank_ind

        return result


    def _turn_json_into_dataset_object(self, a_json):
        dataset = Dataset(chain_for_id=self._org_id, int_for_id=self._dat_int)
        self._dat_int += 1  # updating id int dataset value
        dataset.frequency = Dataset.THREE_YEARS

        self._add_observation_objects(dataset, a_json)
        self._decorate_dataset_with_common_objects(dataset)

        return dataset

    def _decorate_dataset_with_common_objects(self, dataset):
        self._default_datasource.add_dataset(dataset)
        dataset.license_type = self._default_license

    def _add_observation_objects(self, dataset, a_json):
        #Because of the format of the json file, we wiil find the list
        #of the observations in root dict under 'value' key
        observations_list = a_json["value"]
        for obs_dict in observations_list:
            obs_object = self._build_observation_object_from_dict(obs_dict)
            if self._pass_observation_filters(obs_object):
                dataset.add_observation(obs_object)
        #No return needed

    def _pass_observation_filters(self, obs_object):
        # TODO: Unimplemented method. Sure about there can be filters
        # TODO: but not sure about which filters are we going to have
        return True

    def _build_observation_object_from_dict(self, obs_dict):
        result = Observation(chain_for_id=self._org_id, int_for_id=self._obs_int)
        self._obs_int += 1  # Updating obs id int value

        result.indicator = self._get_indicator_of_observation(obs_dict[self.INDICATOR_JSON])
        result.value = self._build_value_of_observation(obs_dict)
        result.computation = self._get_computation_of_observation()  # Always the same, no parameter needed
        result.issued = self._build_issued_object_of_observation()  # No param needed. It should be calculated
        result.ref_time = self._build_ref_time_of_observation(obs_dict)
        #Referring country
        self._join_observation_and_country(result, obs_dict)


        return result

    def _join_observation_and_country(self, obs_object, obs_dict):
        country_key = obs_dict[self.ISO3_JSON]
        try:
            if not country_key in self._countries_dict:
                self._countries_dict[country_key] = self._reconciler.get_country_by_iso3(country_key)
            country_obj = self._countries_dict[country_key]
            country_obj.add_observation(obs_object)
        except UnknownCountryError:
            raise RuntimeError("Unknown country while parsing observation. IDO3: {0}".format(country_key))

    def _build_ref_time_of_observation(self, obs_dict):
        try:
            numeric_date = int(obs_dict[self.YEAR_JSON])
            return YearInterval(year=numeric_date)
        except:
            raise RuntimeError("Error while parsing an obs date. It looks like the date in not well formed: "
                               "Country {0}, Indicator {1}.".format(obs_dict[self.ISO3_JSON], self.INDICATOR_JSON))

    @staticmethod
    def _build_issued_object_of_observation():
        return Instant(datetime.now())

    def _get_computation_of_observation(self):
        return self._default_computation

    def _build_value_of_observation(self, obs_dict):
        result = Value()

        #Deciding type
        if obs_dict[self.INDICATOR_JSON].endswith("_RANK"):  # It means it is a ranking observation
            result.value_type = Value.INTEGER
        else:  # It means it is another kind of numeric observation, but float
            result.value_type = Value.FLOAT

        #Deciding status
        if unicode(obs_dict[self.VALUE_JSON]).isnumeric():  # Means that we have a numeric obs value
            result.obs_status = Value.AVAILABLE
        else:  # It means that we have a string value in observation, indicating 'None" value
            result.obs_status = Value.MISSING

        #Deciding VALUE
        if result.obs_status == Value.MISSING:  # No value
            result.value = None
        elif result.value_type == Value.FLOAT:
            result.value = obs_dict[self.VALUE_JSON]
        elif result.value_type == Value.INTEGER:
            result.value = int(obs_dict[self.VALUE_JSON])
        else:
            raise RuntimeError("Error while parsing value of observation. Country {0}, year {1}, variable {2}" \
                            .format(obs_dict[self.ISO3_JSON], obs_dict[self.YEAR_JSON], obs_dict[self.INDICATOR_JSON]))

        return result


    def _get_indicator_of_observation(self, indicator_key):
        try:
            return self._indicators_dict[indicator_key]
        except:
            raise RuntimeError("Trying to build an unknown indicator: {0}".format(indicator_key))




