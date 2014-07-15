from lpentities.year_interval import YearInterval

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
from lpentities.month_interval import MonthInterval

from .xml_management.rest_xml_tracker import RestXmlTracker
from .xml_management.xml_content_parser import XmlContentParser

from reconciler.country_reconciler import CountryReconciler
from model2xml.model2xml import ModelToXMLTransformer

from ..exceptions.no_new_data_available_error import NoNewDataAvailableError

from datetime import datetime


class FoncierImporter(object):

    TITRES_CREES = 0
    MUTATIONS = 1
    CSJ = 2
    REPERAGES = 3
    BORNAGES = 4
    REP_DES_PLANS = 5


    def __init__(self, log, config, look_for_historical):
        self._log = log
        self._config = config
        self._look_for_historical = look_for_historical
        self._reconciler = CountryReconciler()

        #Initializing variable ids
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

        #Indicators_dict
        self._indicators_dict = self._build_indicators_dict()

        #Building parsing instances
        self._xml_tracker = self._build_xml_tracker()
        self._xml_parser = self._build_xml_parser()

        # Building common objects
        self._default_user = self._build_default_user()  # Done
        self._default_datasource = self._build_default_datasource()  # Done
        self._default_dataset = self._build_default_dataset()  # Done
        self._default_organization = self._build_default_organization()  # Done
        self._default_license = self._build_default_license()  # Done
        self._relate_common_objects()  # Done
        self._default_country = self._get_default_country()  # Done =)
        self._default_computation = Computation(uri=Computation.RAW)




    def run(self):
        """
        Steps:

        This method is going to work as importer and object builder simultaneusly:
        Steps:
         - Build common objects. (In constructor)
         - Consider every data es member of the same dataset. (In constructor)
         - for available years, or needed years,(for every month) call to API. HERE WE STRAT THE RUN
         - Build an obs object for each indicator tracked.
         - Incorpore obs to dataset
         - Send it to model2xml
         - Actualize config values (ids and last checked)
        """
        #Determine years to query
        first_year = last_year = 0
        try:
            first_year, last_year = self._determine_years_to_query()  # Done

        except NoNewDataAvailableError:
            raise RuntimeError("The importer has been executed in non_historical mode, but it looks that "
                               "there are not new data available")

        #Generate observations and incorpore it to the common objects
        observations = self._build_observations_from_available_years(first_year, last_year)
        for obs in observations:
            self._default_dataset.add_observation(obs)

        # Send model for its translation
        try:
            translator = ModelToXMLTransformer(self._default_dataset, ModelToXMLTransformer.API, self._default_user, self._path_to_api())
            translator.run()
            self._actualize_config_values(last_year)
        except BaseException as e:
            raise RuntimeError("Error while sending info to the module receiver: " + e.message)

    def _path_to_api(self):
        return self._config.get("IMPORTER", "url_api")

    def _build_xml_tracker(self):
        return RestXmlTracker(url_pattern_month=self._config.get("IMPORTER", "url_pattern_month"),
                              url_pattern_year=self._config.get("IMPORTER", "url_pattern_year"),
                              year_pattern=self._config.get("IMPORTER", "year_pattern"),
                              month_pattern=self._config.get("IMPORTER", "month_pattern"))

    def _build_xml_parser(self):
        return XmlContentParser(self._log)

    def _actualize_config_values(self, last_year):
        self._config.set("TRANSLATOR", "obs_int", self._obs_int)
        self._config.set("TRANSLATOR", "sli_int", self._sli_int)
        self._config.set("TRANSLATOR", "dat_int", self._dat_int)
        self._config.set("TRANSLATOR", "igr_int", self._igr_int)
        self._config.set("AVAILABLE_TIME", "last_checked_year", last_year)
        with open("./files/configuration.ini", 'wb') as config_file:
            self._config.write(config_file)

    def _build_observations_from_available_years(self, first_year, last_year):
        result = []
        for year in range(first_year, last_year + 1):
            result += self._build_observations_from_a_single_year(year)
        return result

    def _build_observations_from_a_single_year(self, year):
        result = []
        result += self._build_observation_for_a_whole_year(year)
        for month in range(1, 13):
            result += self._build_observation_from_a_concrete_month(year, month)
        return result

    def _build_observation_for_a_whole_year(self, year):
        """
        Steps:
         - Call the API and track the data from a whole year.
         - Turn the xml into an intermediate structure (list or dict)
         - build obs from that structure

        """
        xml_data = self._xml_tracker.track_xml(year, None)
        register = self._xml_parser.turn_xml_into_register(xml_content=xml_data,
                                                           year=year,
                                                           month=None)
        return self._build_observations_from_register(register)


    def _build_observation_from_a_concrete_month(self, year, month):
        """
        Steps:
         - Call the API and track the data from a month
         - Turn the xml into an intermediate structure (list or dict)
         - build obs from that structure

        """
        xml_data = self._xml_tracker.track_xml(year, month)
        register = self._xml_parser.turn_xml_into_register(xml_content=xml_data,
                                                           year=year,
                                                           month=month)
        return self._build_observations_from_register(register)

    def _build_observations_from_register(self, register):
        """
        We have to build 6 observations for each register. An observation per indicator.
        The thing that change

        """
        result = []

        #Titres
        result.append(self._build_observation_for_a_given_indicator_and_value(
            self._indicators_dict[self.TITRES_CREES],
            register.mutations,
            register.year,
            register.month))
        #Mutations
        result.append(self._build_observation_for_a_given_indicator_and_value(
            self._indicators_dict[self.MUTATIONS],
            register.mutations,
            register.year,
            register.month))
        #Csj
        result.append(self._build_observation_for_a_given_indicator_and_value(
            self._indicators_dict[self.CSJ],
            register.csj,
            register.year,
            register.month))
        #Reperages
        result.append(self._build_observation_for_a_given_indicator_and_value(
            self._indicators_dict[self.REPERAGES],
            register.reperages,
            register.year,
            register.month))
        #Bornages
        result.append(self._build_observation_for_a_given_indicator_and_value(
            self._indicators_dict[self.BORNAGES],
            register.bornages,
            register.year,
            register.month))
        #Reproduction des plans
        result.append(self._build_observation_for_a_given_indicator_and_value(
            self._indicators_dict[self.REP_DES_PLANS],
            register.reproduction_des_plans,
            register.year,
            register.month))

        return result

    def _build_observation_for_a_given_indicator_and_value(self, indicator, value, year, month):
        """
        It is expected to receive an indicator object completely built and a numeric value.
        Also needs an year and a month value.
        It should produce an observation completely built and properly related with the rest
        of the model objects

        """
        result = Observation(chain_for_id=self._org_id, int_for_id=self._obs_int)
        self._obs_int += 1  # Updating id value
        result.indicator = indicator
        result.value = self._build_value_object(value)
        result.computation = self._get_computation_object()  # Always the same, no param needed
        result.issued = self._build_issued_object()  # No param needed
        result.ref_time = self._build_ref_time_object(year, month)
        self._default_country.add_observation(result)  # And that stablish therelation in both directions

        return result

    @staticmethod
    def _build_ref_time_object(year, month):
        if month is not None:
            return MonthInterval(year=year, month=month)
        else:
            return YearInterval(year=year)

    def _build_issued_object(self):
        return Instant(datetime.now())


    def _get_computation_object(self):
        return self._default_computation

    @staticmethod
    def _build_value_object(value):
        if not (value is None or value == ""):
            return Value(value=value,
                         value_type=Value.INTEGER,
                         obs_status=Value.AVAILABLE)
        else:
            return Value(value=None,
                         value_type=Value.INTEGER,
                         obs_status=Value.MISSING)

    def _determine_years_to_query(self):
        first_year = int(self._config.get("AVAILABLE_TIME", "first_year"))
        last_year = int(self._config.get("AVAILABLE_TIME", "last_year"))

        if self._look_for_historical:
            return first_year, last_year
        else:
            last_checked = int(self._config.get("AVAILABLE_TIME", "last_checked_year"))
            if last_year <= last_checked:
                raise NoNewDataAvailableError("No new data available. Source has not been updated since last execution")
            else:
                return last_checked, last_year




    def _get_default_country(self):
        return self._reconciler.get_country_by_iso3("MDG")

    def _build_default_user(self):
        return User(user_login="FONCIERIMPORTER")

    def _build_default_datasource(self):
        result = DataSource(chain_for_id=self._org_id, int_for_id=self._config.get("DATASOURCE", "id"))
        result.name = self._config.get("DATASOURCE", "name")
        return result

    def _build_default_dataset(self):
        result = Dataset(chain_for_id=self._org_id, int_for_id=self._dat_int)
        self._dat_int += 1  # Needed increment
        result.frequency = Dataset.YEARLY
        return result

    def _build_default_organization(self):
        result = Organization(chain_for_id=self._org_id)
        result.name = self._config.get("ORGANIZATION", "name")
        result.url = self._config.get("ORGANIZATION", "url")
        result.url_logo = self._config.get("ORGANIZATION", "url_logo")
        result.description_en = self._read_config_value("ORGANIZATION", "description_en")
        result.description_es = self._read_config_value("ORGANIZATION", "description_es")
        result.description_fr = self._read_config_value("ORGANIZATION", "description_fr")

        return result


    def _build_default_license(self):
        result = License()
        result.republish = self._config.get("LICENSE", "republish")
        result.description = self._config.get("LICENSE", "description")
        result.name = self._config.get("LICENSE", "name")
        result.url = self._config.get("LICENSE", "url")

        return result

    def _build_indicators_dict(self):
        result = {}
        default_measurement_unit = MeasurementUnit(name="Units",
                                                   convert_to=MeasurementUnit.UNITS,
                                                   factor=1)
        #Titres crees
        titres_crees_ind = Indicator(chain_for_id=self._org_id,
                                     int_for_id=self._config.get("INDICATOR", "titres_id"))
        titres_crees_ind.name_en = self._read_config_value("INDICATOR", "titres_name_en")
        titres_crees_ind.name_es = self._read_config_value("INDICATOR", "titres_name_es")
        titres_crees_ind.name_fr = self._read_config_value("INDICATOR", "titres_name_fr")
        titres_crees_ind.description_en = self._read_config_value("INDICATOR", "titres_desc_en")
        titres_crees_ind.description_es = self._read_config_value("INDICATOR", "titres_desc_es")
        titres_crees_ind.description_fr = self._read_config_value("INDICATOR", "titres_desc_fr")
        titres_crees_ind.measurement_unit = default_measurement_unit
        titres_crees_ind.topic = 'LAND_USE'
        titres_crees_ind.preferable_tendency = Indicator.IRRELEVANT

        result[self.TITRES_CREES] = titres_crees_ind

        #Mutations
        mutations_ind = Indicator(chain_for_id=self._org_id,
                                  int_for_id=self._config.get("INDICATOR", "mutations_id"))
        mutations_ind.name_en = self._read_config_value("INDICATOR", "mutations_name_en")
        mutations_ind.name_es = self._read_config_value("INDICATOR", "mutations_name_es")
        mutations_ind.name_fr = self._read_config_value("INDICATOR", "mutations_name_fr")
        mutations_ind.description_en = self._read_config_value("INDICATOR", "mutations_desc_en")
        mutations_ind.description_es = self._read_config_value("INDICATOR", "mutations_desc_es")
        mutations_ind.description_fr = self._read_config_value("INDICATOR", "mutations_desc_fr")
        mutations_ind.measurement_unit = default_measurement_unit
        mutations_ind.topic = 'LAND_USE'
        mutations_ind.preferable_tendency = Indicator.IRRELEVANT

        result[self.MUTATIONS] = mutations_ind

        #CSJ
        csj_ind = Indicator(chain_for_id=self._org_id,
                            int_for_id=self._config.get("INDICATOR", "csj_id"))
        csj_ind.name_en = self._read_config_value("INDICATOR", "csj_name_en")
        csj_ind.name_es = self._read_config_value("INDICATOR", "csj_name_es")
        csj_ind.name_fr = self._read_config_value("INDICATOR", "csj_name_fr")
        csj_ind.description_en = self._read_config_value("INDICATOR", "csj_desc_en")
        csj_ind.description_es = self._read_config_value("INDICATOR", "csj_desc_es")
        csj_ind.description_fr = self._read_config_value("INDICATOR", "csj_desc_fr")
        csj_ind.measurement_unit = default_measurement_unit
        csj_ind.topic = 'LAND_USE'
        csj_ind.preferable_tendency = Indicator.IRRELEVANT

        result[self.CSJ] = csj_ind

        #Reperages
        reperages_ind = Indicator(chain_for_id=self._org_id,
                                  int_for_id=self._config.get("INDICATOR", "reperages_id"))
        reperages_ind.name_en = self._read_config_value("INDICATOR", "reperages_name_en")
        reperages_ind.name_es = self._read_config_value("INDICATOR", "reperages_name_es")
        reperages_ind.name_fr = self._read_config_value("INDICATOR", "reperages_name_fr")
        reperages_ind.description_en = self._read_config_value("INDICATOR", "reperages_desc_en")
        reperages_ind.description_es = self._read_config_value("INDICATOR", "reperages_desc_es")
        reperages_ind.description_fr = self._read_config_value("INDICATOR", "reperages_desc_fr")
        reperages_ind.topic = 'LAND_USE'
        reperages_ind.measurement_unit = default_measurement_unit
        reperages_ind.preferable_tendency = Indicator.IRRELEVANT

        result[self.REPERAGES] = reperages_ind

        #Bornages
        bornages_ind = Indicator(chain_for_id=self._org_id,
                                 int_for_id=self._config.get("INDICATOR", "bornages_id"))
        bornages_ind.name_en = self._read_config_value("INDICATOR", "bornages_name_en")
        bornages_ind.name_es = self._read_config_value("INDICATOR", "bornages_name_es")
        bornages_ind.name_fr = self._read_config_value("INDICATOR", "bornages_name_fr")
        bornages_ind.description_en = self._read_config_value("INDICATOR", "bornages_desc_en")
        bornages_ind.description_es = self._read_config_value("INDICATOR", "bornages_desc_es")
        bornages_ind.description_fr = self._read_config_value("INDICATOR", "bornages_desc_fr")
        bornages_ind.topic = 'LAND_USE'
        bornages_ind.measurement_unit = default_measurement_unit
        bornages_ind.preferable_tendency = Indicator.IRRELEVANT

        result[self.BORNAGES] = bornages_ind

        #Rep_des_plans
        rep_des_plans_ind = Indicator(chain_for_id=self._org_id,
                                      int_for_id=self._config.get("INDICATOR", "rep_des_plans_id"))
        rep_des_plans_ind.name_en = self._read_config_value("INDICATOR", "rep_des_plans_name_en")
        rep_des_plans_ind.name_es = self._read_config_value("INDICATOR", "rep_des_plans_name_es")
        rep_des_plans_ind.name_fr = self._read_config_value("INDICATOR", "rep_des_plans_name_fr")
        rep_des_plans_ind.description_en = self._read_config_value("INDICATOR", "rep_des_plans_desc_en")
        rep_des_plans_ind.description_es = self._read_config_value("INDICATOR", "rep_des_plans_desc_es")
        rep_des_plans_ind.description_fr = self._read_config_value("INDICATOR", "rep_des_plans_desc_fr")
        rep_des_plans_ind.topic = 'LAND_USE'
        rep_des_plans_ind.measurement_unit = default_measurement_unit
        rep_des_plans_ind.preferable_tendency = Indicator.IRRELEVANT

        result[self.REP_DES_PLANS] = rep_des_plans_ind

        #Returning final dict
        return result

    def _read_config_value(self, section, field):
        return (self._config.get(section, field)).decode(encoding="utf-8")


    def _relate_common_objects(self):
        self._default_organization.add_user(self._default_user)
        self._default_organization.add_data_source(self._default_datasource)
        self._default_datasource.add_dataset(self._default_dataset)
        self._default_dataset.license_type = self._default_license
        #No return needed
