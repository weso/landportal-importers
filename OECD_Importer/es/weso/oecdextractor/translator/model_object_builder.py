from datetime import datetime
from es.weso.oecdextractor.translator.json_loader import JsonLoader
from es.weso.oecdextractor.translator.path_object_pair import PathObjectPair

from lpentities.computation import Computation
from lpentities.data_source import DataSource
from lpentities.dataset import Dataset
from lpentities.indicator import Indicator
from lpentities.indicator_relationship import IndicatorRelationship
from lpentities.instant import Instant
from lpentities.license import License
from lpentities.measurement_unit import MeasurementUnit
from lpentities.observation import Observation
from lpentities.organization import Organization
from lpentities.user import User
from lpentities.value import Value
from lpentities.year_interval import YearInterval
from reconciler.country_reconciler import CountryReconciler
from reconciler.exceptions.unknown_country_error import UnknownCountryError

from .indicator_key_mapper import KeyMapper


__author__ = 'Dani'


class ModelObjectBuilder(object):

    INDICATOR_JSON = "VARIABLE"
    ISO3_JSON = "LOCATION"
    VALUE_JSON = "Value"

    #Depending on the json file, the concept "year" could be referred with one of the next:
    YEAR_JSON = "YEAR"
    TIME_JSON = "TIME"




    def __init__(self, log, config, look_for_historical):
        self._log = log
        self._config = config
        self._look_for_historical = look_for_historical
        self._json_pairs = JsonLoader(self._log, self._config).run()



        # Getting propper ids
        self._org_id = self._config.get("TRANSLATOR", "org_id")
        self._first_valid_year = int(self._config.get("HISTORICAL", "first_valid_year"))
        self._last_checked_year = self._first_valid_year - 1
        if not look_for_historical:
            self._obs_int = int(self._config.get("TRANSLATOR", "obs_int"))
            self._sli_int = int(self._config.get("TRANSLATOR", "sli_int"))
            self._igr_int = int(self._config.get("TRANSLATOR", "igr_int"))
            self._dat_int = int(self._config.get("TRANSLATOR", "dat_int"))
        else:
            self._obs_int = 0
            self._sli_int = 0
            self._igr_int = 0
            self._dat_int = 0

        # Creating objects that would be necessary during the construction of the model
        self._indicators_dict = self._build_indicators_dict()
        self._indicator_relations = self._build_indicator_relations()
        self._default_computation = self._build_default_computation()
        self._countries_dict = {}  # It will be completed during the parsing process
        self._reconciler = CountryReconciler()
        self._default_user = self._build_default_user()
        self._default_organization = self._build_default_organization()
        self._default_datasource = self._build_default_datasource()
        self._default_license = self._build_default_license()
        self.relate_common_objects()

    def actualize_config_values(self):
        self._config.set("TRANSLATOR", "obs_int", self._obs_int)
        self._config.set("TRANSLATOR", "sli_int", self._sli_int)
        self._config.set("TRANSLATOR", "igr_int", self._igr_int)
        self._config.set("TRANSLATOR", "dat_int", self._dat_int)

        self._config.set("HISTORICAL", "first_valid_year", self._last_checked_year + 1)


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
        result.description_en = self._read_config_value("ORGANIZATION", "oecd_desc_en")
        result.description_es = self._read_config_value("ORGANIZATION", "oecd_desc_es")
        result.description_fr = self._read_config_value("ORGANIZATION", "oecd_desc_fr")
        result.url_logo = self._read_config_value("ORGANIZATION", "oecd_url_logo")

        return result

    def _build_default_datasource(self):
        result = DataSource(chain_for_id=self._org_id, int_for_id=int(self._config.get("DATASOURCE", "datasource_id")))
        result.name = self._config.get("DATASOURCE", "datasource_name")

        self._dat_int += 1  # Updating int id dataset value
        return result

    def _build_default_user(self):
        return User(user_login=self._config.get("USER", "user_name"))

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
        for a_pair in self._json_pairs:
            result.append(PathObjectPair(a_pair.file_path,
                                         self._turn_json_into_dataset_object(a_pair.other_object)))
        return result, self._default_user, self._indicator_relations

    @staticmethod
    def _build_default_computation():
        return Computation(Computation.RAW)

    def _build_indicators_dict(self):
        result = {}

        #Prepearing measurement units
        index_unit = MeasurementUnit(name="0 to 1 index", convert_to="index")
        rank_unit = MeasurementUnit(name="rank", convert_to="rank")


        #SIGI
        sigi_ind = Indicator(chain_for_id=self._org_id,
                             int_for_id=int(self._read_config_value("INDICATORS", "sigi_id")))
        sigi_ind.name_en = self._read_config_value("INDICATORS", "sigi_name_en")
        sigi_ind.name_es = self._read_config_value("INDICATORS", "sigi_name_es")
        sigi_ind.name_fr = self._read_config_value("INDICATORS", "sigi_name_fr")
        sigi_ind.description_en = self._read_config_value("INDICATORS", "sigi_desc_en")
        sigi_ind.description_es = self._read_config_value("INDICATORS", "sigi_desc_es")
        sigi_ind.description_fr = self._read_config_value("INDICATORS", "sigi_desc_fr")
        sigi_ind.topic = self._read_config_value("INDICATORS", "sigi_topic")
        sigi_ind.measurement_unit = index_unit
        sigi_ind.preferable_tendency = Indicator.DECREASE
        result[KeyMapper.SIGI_KEY] = sigi_ind

        #SIGI RANK
        sigi_rank_ind = Indicator(chain_for_id=self._org_id,
                             int_for_id=int(self._read_config_value("INDICATORS", "sigi_rank_id")))
        sigi_rank_ind.name_en = self._read_config_value("INDICATORS", "sigi_rank_name_en")
        sigi_rank_ind.name_es = self._read_config_value("INDICATORS", "sigi_rank_name_es")
        sigi_rank_ind.name_fr = self._read_config_value("INDICATORS", "sigi_rank_name_fr")
        sigi_rank_ind.description_en = self._read_config_value("INDICATORS", "sigi_rank_desc_en")
        sigi_rank_ind.description_es = self._read_config_value("INDICATORS", "sigi_rank_desc_es")
        sigi_rank_ind.description_fr = self._read_config_value("INDICATORS", "sigi_rank_desc_fr")
        sigi_rank_ind.topic = self._read_config_value("INDICATORS", "sigi_rank_topic")
        sigi_rank_ind.measurement_unit = rank_unit
        sigi_rank_ind.preferable_tendency = Indicator.DECREASE
        result[KeyMapper.SIGI_RANK_KEY] = sigi_rank_ind


        #FC
        fc_ind = Indicator(chain_for_id=self._org_id,
                        int_for_id=int(self._read_config_value("INDICATORS", "fc_id")))
        fc_ind.name_en = self._read_config_value("INDICATORS", "fc_name_en")
        fc_ind.name_es = self._read_config_value("INDICATORS", "fc_name_es")
        fc_ind.name_fr = self._read_config_value("INDICATORS", "fc_name_fr")
        fc_ind.description_en = self._read_config_value("INDICATORS", "fc_rank_name_en")
        fc_ind.description_es = self._read_config_value("INDICATORS", "fc_rank_name_es")
        fc_ind.description_fr = self._read_config_value("INDICATORS", "fc_rank_name_fr")
        fc_ind.topic = self._read_config_value("INDICATORS", "fc_topic")
        fc_ind.measurement_unit = index_unit
        fc_ind.preferable_tendency = Indicator.DECREASE
        result[KeyMapper.FAMILY_CODE_KEY] = fc_ind

        #FC RANK
        fc_rank_ind = Indicator(chain_for_id=self._org_id,
                             int_for_id=int(self._read_config_value("INDICATORS", "fc_rank_id")))
        fc_rank_ind.name_en = self._read_config_value("INDICATORS", "fc_rank_name_en")
        fc_rank_ind.name_es = self._read_config_value("INDICATORS", "fc_rank_name_es")
        fc_rank_ind.name_fr = self._read_config_value("INDICATORS", "fc_rank_name_fr")
        fc_rank_ind.description_en = self._read_config_value("INDICATORS", "fc_rank_name_en")
        fc_rank_ind.description_es = self._read_config_value("INDICATORS", "fc_rank_name_es")
        fc_rank_ind.description_fr = self._read_config_value("INDICATORS", "fc_rank_name_fr")
        fc_rank_ind.topic = self._read_config_value("INDICATORS", "fc_rank_topic")
        fc_rank_ind.measurement_unit = rank_unit
        fc_rank_ind.preferable_tendency = Indicator.DECREASE
        result[KeyMapper.FAMILY_CODE_RANK_KEY] = fc_rank_ind

        #CIVIL
        civil_ind = Indicator(chain_for_id=self._org_id,
                             int_for_id=int(self._read_config_value("INDICATORS", "civil_id")))
        civil_ind.name_en = self._read_config_value("INDICATORS", "civil_name_en")
        civil_ind.name_es = self._read_config_value("INDICATORS", "civil_name_es")
        civil_ind.name_fr = self._read_config_value("INDICATORS", "civil_name_fr")
        civil_ind.description_en = self._read_config_value("INDICATORS", "civil_rank_name_en")
        civil_ind.description_es = self._read_config_value("INDICATORS", "civil_rank_name_es")
        civil_ind.description_fr = self._read_config_value("INDICATORS", "civil_rank_name_fr")
        civil_ind.topic = self._read_config_value("INDICATORS", "civil_topic")
        civil_ind.measurement_unit = index_unit
        civil_ind.preferable_tendency = Indicator.DECREASE
        result[KeyMapper.CIVIL_KEY] = civil_ind

        #CIVIL RANK
        civil_rank_ind = Indicator(chain_for_id=self._org_id,
                             int_for_id=int(self._read_config_value("INDICATORS", "civil_rank_id")))
        civil_rank_ind.name_en = self._read_config_value("INDICATORS", "civil_rank_name_en")
        civil_rank_ind.name_es = self._read_config_value("INDICATORS", "civil_rank_name_es")
        civil_rank_ind.name_fr = self._read_config_value("INDICATORS", "civil_rank_name_fr")
        civil_rank_ind.description_en = self._read_config_value("INDICATORS", "civil_rank_name_en")
        civil_rank_ind.description_es = self._read_config_value("INDICATORS", "civil_rank_name_es")
        civil_rank_ind.description_fr = self._read_config_value("INDICATORS", "civil_rank_name_fr")
        civil_rank_ind.measurement_unit = rank_unit
        civil_rank_ind.topic = self._read_config_value("INDICATORS", "civil_rank_topic")
        civil_rank_ind.preferable_tendency = Indicator.DECREASE
        result[KeyMapper.CIVIL_RANK_KEY] = civil_rank_ind


        #ENTITLEMENTS
        entitlements_ind = Indicator(chain_for_id=self._org_id,
                             int_for_id=int(self._read_config_value("INDICATORS", "entitlements_id")))
        entitlements_ind.name_en = self._read_config_value("INDICATORS", "entitlements_name_en")
        entitlements_ind.name_es = self._read_config_value("INDICATORS", "entitlements_name_es")
        entitlements_ind.name_fr = self._read_config_value("INDICATORS", "entitlements_name_fr")
        entitlements_ind.description_en = self._read_config_value("INDICATORS", "entitlements_name_en")
        entitlements_ind.description_es = self._read_config_value("INDICATORS", "entitlements_name_es")
        entitlements_ind.description_fr = self._read_config_value("INDICATORS", "entitlements_name_fr")
        entitlements_ind.measurement_unit = index_unit
        entitlements_ind.topic = self._read_config_value("INDICATORS", "entitlements_topic")
        entitlements_ind.preferable_tendency = Indicator.DECREASE
        result[KeyMapper.ENTITLEMENTS_KEY] = entitlements_ind

        #ENTITLEMENTS RANK
        entitlements_rank_ind = Indicator(chain_for_id=self._org_id,
                             int_for_id=int(self._read_config_value("INDICATORS", "entitlements_rank_id")))
        entitlements_rank_ind.name_en = self._read_config_value("INDICATORS", "entitlements_rank_name_en")
        entitlements_rank_ind.name_es = self._read_config_value("INDICATORS", "entitlements_rank_name_es")
        entitlements_rank_ind.name_fr = self._read_config_value("INDICATORS", "entitlements_rank_name_fr")
        entitlements_rank_ind.description_en = self._read_config_value("INDICATORS", "entitlements_rank_name_en")
        entitlements_rank_ind.description_es = self._read_config_value("INDICATORS", "entitlements_rank_name_es")
        entitlements_rank_ind.description_fr = self._read_config_value("INDICATORS", "entitlements_rank_name_fr")
        entitlements_rank_ind.measurement_unit = rank_unit
        entitlements_rank_ind.topic = self._read_config_value("INDICATORS", "entitlements_rank_topic")
        entitlements_rank_ind.preferable_tendency = Indicator.DECREASE
        result[KeyMapper.ENTITLEMENTS_RANK_KEY] = entitlements_rank_ind

        #ACCESS TO LAND
        women_land_access_ind = Indicator(chain_for_id=self._org_id,
                             int_for_id=int(self._read_config_value("INDICATORS", "women_land_access_id")))
        women_land_access_ind.name_en = self._read_config_value("INDICATORS", "women_land_access_name_en")
        women_land_access_ind.name_es = self._read_config_value("INDICATORS", "women_land_access_name_es")
        women_land_access_ind.name_fr = self._read_config_value("INDICATORS", "women_land_access_name_fr")
        women_land_access_ind.description_en = self._read_config_value("INDICATORS", "women_land_access_name_en")
        women_land_access_ind.description_es = self._read_config_value("INDICATORS", "women_land_access_name_es")
        women_land_access_ind.description_fr = self._read_config_value("INDICATORS", "women_land_access_name_fr")
        women_land_access_ind.measurement_unit = index_unit
        women_land_access_ind.topic = self._read_config_value("INDICATORS", "women_land_access_topic")
        women_land_access_ind.preferable_tendency = Indicator.DECREASE
        result[KeyMapper.LAND_KEY] = women_land_access_ind

        #INHERITANCE GENERAL
        inheritance_general_ind = Indicator(chain_for_id=self._org_id,
                             int_for_id=int(self._read_config_value("INDICATORS", "inheritance_general_id")))
        inheritance_general_ind.name_en = self._read_config_value("INDICATORS", "inheritance_general_name_en")
        inheritance_general_ind.name_es = self._read_config_value("INDICATORS", "inheritance_general_name_es")
        inheritance_general_ind.name_fr = self._read_config_value("INDICATORS", "inheritance_general_name_fr")
        inheritance_general_ind.description_en = self._read_config_value("INDICATORS", "inheritance_general_name_en")
        inheritance_general_ind.description_es = self._read_config_value("INDICATORS", "inheritance_general_name_es")
        inheritance_general_ind.description_fr = self._read_config_value("INDICATORS", "inheritance_general_name_fr")
        inheritance_general_ind.measurement_unit = index_unit
        inheritance_general_ind.topic = self._read_config_value("INDICATORS", "inheritance_general_topic")
        inheritance_general_ind.preferable_tendency = Indicator.DECREASE
        result[KeyMapper.INHERITANCE_GENERAL_KEY] = inheritance_general_ind

        #INHERITANCE DAUGHTERS
        inheritance_daughters_ind = Indicator(chain_for_id=self._org_id,
                             int_for_id=int(self._read_config_value("INDICATORS", "inheritance_daughters_id")))
        inheritance_daughters_ind.name_en = self._read_config_value("INDICATORS", "inheritance_daughters_name_en")
        inheritance_daughters_ind.name_es = self._read_config_value("INDICATORS", "inheritance_daughters_name_es")
        inheritance_daughters_ind.name_fr = self._read_config_value("INDICATORS", "inheritance_daughters_name_fr")
        inheritance_daughters_ind.description_en = self._read_config_value("INDICATORS", "inheritance_daughters_name_en")
        inheritance_daughters_ind.description_es = self._read_config_value("INDICATORS", "inheritance_daughters_name_es")
        inheritance_daughters_ind.description_fr = self._read_config_value("INDICATORS", "inheritance_daughters_name_fr")
        inheritance_daughters_ind.measurement_unit = index_unit
        inheritance_daughters_ind.topic = self._read_config_value("INDICATORS", "inheritance_daughters_topic")
        inheritance_daughters_ind.preferable_tendency = Indicator.DECREASE
        result[KeyMapper.INHERITANCE_DAUGHTERS_KEY] = inheritance_daughters_ind

        #INHERITANCE WIDOWS
        inheritance_widows_ind = Indicator(chain_for_id=self._org_id,
                             int_for_id=int(self._read_config_value("INDICATORS", "inheritance_widows_id")))
        inheritance_widows_ind.name_en = self._read_config_value("INDICATORS", "inheritance_widows_name_en")
        inheritance_widows_ind.name_es = self._read_config_value("INDICATORS", "inheritance_widows_name_es")
        inheritance_widows_ind.name_fr = self._read_config_value("INDICATORS", "inheritance_widows_name_fr")
        inheritance_widows_ind.description_en = self._read_config_value("INDICATORS", "inheritance_widows_name_en")
        inheritance_widows_ind.description_es = self._read_config_value("INDICATORS", "inheritance_widows_name_es")
        inheritance_widows_ind.description_fr = self._read_config_value("INDICATORS", "inheritance_widows_name_fr")
        inheritance_widows_ind.measurement_unit = index_unit
        inheritance_widows_ind.topic = self._read_config_value("INDICATORS", "inheritance_widows_topic")
        inheritance_widows_ind.preferable_tendency = Indicator.DECREASE
        result[KeyMapper.INHERITANCE_WIDOWS_KEY] = inheritance_widows_ind

        return result

    def _read_config_value(self, section, field):
        return (self._config.get(section, field)).decode(encoding="utf-8")

    def _build_indicator_relations(self):
        result = [
            IndicatorRelationship(source=self._indicators_dict[KeyMapper.INHERITANCE_GENERAL_KEY],
                                  target=self._indicators_dict[KeyMapper.INHERITANCE_DAUGHTERS_KEY]),
            IndicatorRelationship(source=self._indicators_dict[KeyMapper.INHERITANCE_GENERAL_KEY],
                                  target=self._indicators_dict[KeyMapper.INHERITANCE_WIDOWS_KEY])
        ]
        return result


    def _turn_json_into_dataset_object(self, a_json):
        dataset = Dataset(chain_for_id=self._org_id, int_for_id=self._dat_int)
        self._dat_int += 1  # updating id int dataset value

        dataset.frequency = Dataset.THREE_YEARS

        self._add_observation_objects(dataset, a_json)
        self._decorate_dataset_with_common_objects(dataset)
        self._include_all_indicators(dataset)

        return dataset


    def _include_all_indicators(self, dataset):
        for key in self._indicators_dict:
            dataset.add_indicator(self._indicators_dict[key])

    def _decorate_dataset_with_common_objects(self, dataset):
        self._default_datasource.add_dataset(dataset)
        dataset.license_type = self._default_license

    def _add_observation_objects(self, dataset, a_json):
        #Because of the format of the json file, we wiil find the list
        #of the observations in root dict under 'value' key
        oecd_id_of_dataset = KeyMapper.identify_dataset(a_json["odata.metadata"])
        observations_list = a_json["value"]
        for obs_dict in observations_list:
            try:
                obs_object = self._build_observation_object_from_dict(obs_dict, oecd_id_of_dataset)
                if self._pass_observation_filters(obs_object):
                    dataset.add_observation(obs_object)
            except RuntimeError as e:
                self._log.warning("Observation ignored. " + e.message)
        #No return needed

    def _pass_observation_filters(self, obs_object):
        if self._look_for_historical:
            return True
        else:
            if int(obs_object.ref_time.get_time_string()) < self._first_valid_year:
                return False
            return True


    def _build_observation_object_from_dict(self, obs_dict, oecd_id_of_dataset):
        result = Observation(chain_for_id=self._org_id, int_for_id=self._obs_int)
        self._obs_int += 1  # Updating obs id int value

        result.indicator = self._get_indicator_of_observation(obs_dict[self.INDICATOR_JSON], oecd_id_of_dataset)
        result.value = self._build_value_of_observation(obs_dict)
        result.computation = self._get_computation_of_observation()  # Always the same, no parameter needed
        result.issued = self._build_issued_object_of_observation()  # No param needed. It should be calculated
        result.ref_time = self._build_ref_time_of_observation(obs_dict)
        self._actualize_last_checked_if_needed(result)
        #Referring country
        self._join_observation_and_country(result, obs_dict)


        return result

    def _actualize_last_checked_if_needed(self, observation):
        int_year = int(observation.ref_time.year)  # We can do that because we expect ref-time to be a YearInterval
        if int_year > self._last_checked_year:
            self._last_checked_year = int_year

    def _join_observation_and_country(self, obs_object, obs_dict):
        country_key = obs_dict[self.ISO3_JSON]
        try:
            if not country_key in self._countries_dict:
                self._countries_dict[country_key] = self._reconciler.get_country_by_iso3(country_key)
            country_obj = self._countries_dict[country_key]
            country_obj.add_observation(obs_object)
        except UnknownCountryError:
            raise RuntimeError("Unknown country while parsing observation. ISO3: {0}".format(country_key))

    def _build_ref_time_of_observation(self, obs_dict):
        """
        Depending on the parsed file, the concept 'Year' could be referred through YEAR_JONS or TIME_JSON
        It could be a good ugly, but we must use code that fit in both cases. Using regex here to produce
        general solutions could be a bit exaggerated.

        """
        try:
            if self.YEAR_JSON in obs_dict:
                numeric_date = int(obs_dict[self.YEAR_JSON])
                return YearInterval(year=numeric_date)
            elif self.TIME_JSON in obs_dict:
                numeric_date = int(obs_dict[self.TIME_JSON])
                return YearInterval(year=numeric_date)
            else:
                raise RuntimeError("Error while parsing an obs. Ir looks that it has not got an asociated date."
                                   "Country {0}, indicator {1}".format(obs_dict[self.ISO3_JSON],
                                                                       obs_dict[self.INDICATOR_JSON]))
        except KeyError:
            raise RuntimeError("Error while parsing an obs date. It looks like the date in not well formed: "
                               "Country {0}, Indicator {1}.".format(obs_dict[self.ISO3_JSON],
                                                                    obs_dict[self.INDICATOR_JSON]))

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
        if type(obs_dict[self.VALUE_JSON])in [type(1.0), type(1)]:  # Means that we have a numeric obs value
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
            raise RuntimeError("Error while parsing value of observation. Country {0}, variable {2}".
                               format(obs_dict[self.ISO3_JSON], obs_dict[self.INDICATOR_JSON]))

        return result


    def _get_indicator_of_observation(self, indicator_key, oecd_id_of_dataset):
        try:
            mapped_key = KeyMapper.map_key(key=indicator_key,
                                     dataset_id=oecd_id_of_dataset)
            return self._indicators_dict[mapped_key]
        except:
            raise RuntimeError("Trying to build an unknown indicator: {0}, dataset {1}".format(indicator_key,
                                                                                               oecd_id_of_dataset))




