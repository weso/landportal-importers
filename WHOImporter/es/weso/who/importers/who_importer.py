from datetime import datetime

from lpentities.computation import Computation
from lpentities.data_source import DataSource
from lpentities.dataset import Dataset
from lpentities.indicator import Indicator
from lpentities.instant import Instant
from lpentities.license import License
from lpentities.measurement_unit import MeasurementUnit
from lpentities.month_interval import MonthInterval
from lpentities.observation import Observation
from lpentities.organization import Organization
from lpentities.user import User
from lpentities.value import Value
from model2xml.model2xml import ModelToXMLTransformer
from reconciler.country_reconciler import CountryReconciler

from es.weso.who.exceptions.no_new_data_available_error import NoNewDataAvailableError

from .data_management.csv_downloader import CsvDownloader
from .data_management.indicator_endpoint import IndicatorEndpoint

__author__ = 'BorjaGB'





class WhoImporter(object):

    GNI = 0

    def __init__(self, log, config, look_for_historical):
        self._log = log
        self._config = config
        self._look_for_historical = look_for_historical
        self._reconciler = CountryReconciler()

        #Initializing variable ids
        self._org_id = self._config.get("TRANSLATOR", "org_id")
        self._obs_int = int(self._config.get("TRANSLATOR", "obs_int"))
        self._sli_int = int(self._config.get("TRANSLATOR", "sli_int"))
        self._dat_int = int(self._config.get("TRANSLATOR", "dat_int"))
        self._igr_int = int(self._config.get("TRANSLATOR", "igr_int"))
        self._ind_int = int(self._config.get("TRANSLATOR", "ind_int"))
        self._sou_int = int(self._config.get("TRANSLATOR", "sou_int"))

        #Indicators_dict
        self._indicators_dict = self._build_indicators_dict()
        self._indicators_endpoints = self._build_indicators_endpoint()
        
        #Building parsing instances
        self._csv_downloader = self._build_csv_downloader()
        
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

        This method is going to work as importer and object builder simultaneously:
        Steps:
         - Build common objects. (In constructor)
         - Consider every data as a member of the same dataset. (In constructor)
         - for available years, or needed years,(for every month) call to API. HERE WE START THE RUN
         - Build an observation object for each indicator tracked.
         - Add observation to dataset
         - Send it to model2xml
         - Actualize config values (ids and last checked)
        """
        #Determine years to query
        first_year = last_year = 0
        try:
            first_year, last_year = self._determine_years_to_query()  # Done

        except NoNewDataAvailableError:
            #TODO: make something noisy
            print "NO NEW DATA AVAILABLE"  # Provisional Strategy
            return  # It is quite noisy eh?

        #Generate observations and add it to the common objects
        self._download_csvs()

        #And it is done. No return needed

    def _build_csv_downloader(self):
        return CsvDownloader(url_pattern=self._config.get("IMPORTER", "url_pattern"),
                              indicator_pattern=self._config.get("IMPORTER", "indicator_pattern"),
                              profile_pattern=self._config.get("IMPORTER", "profile_pattern"),
                              countries_pattern=self._config.get("IMPORTER", "countries_pattern"),
                              region_pattern=self._config.get("IMPORTER", "region_pattern"))

    def _build_xml_parser(self):
        return True
    
    def _actualize_config_values(self, last_year):
        self._config.set("TRANSLATOR", "org_id", self._org_id)
        self._config.set("TRANSLATOR", "obs_int", self._obs_int)
        self._config.set("TRANSLATOR", "sli_int", self._sli_int)
        self._config.set("TRANSLATOR", "dat_int", self._dat_int)
        self._config.set("TRANSLATOR", "igr_int", self._igr_int)
        self._config.set("TRANSLATOR", "ind_int", self._ind_int)
        self._config.set("TRANSLATOR", "sou_int", self._sou_int)
        self._config.set("AVAILABLE_TIME", "last_checked_year", last_year)

    def _download_csvs(self):
        print "Downloading CSVs!"
        for ind_end in self._indicators_endpoints:
            print "Downloading indicator: " + self._indicators_endpoints[ind_end].code
            if self._csv_downloader.download_csv(self._indicators_endpoints[ind_end].code, self._indicators_endpoints[ind_end].profile, self._indicators_endpoints[ind_end].countries, self._indicators_endpoints[ind_end].regions, self._indicators_endpoints[ind_end].file_name) :
                print "Yay!"
            else:
                print "ERROR downloading: " + ind_end.file_name

    @staticmethod
    def _build_ref_time_object(year, month):
        return MonthInterval(year=year, month=month)

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
                         obs_status=Value)

    def _determine_years_to_query(self):
        first_year = int(self._config.get("AVAILABLE_TIME", "first_year"))
        last_year = int(self._config.get("AVAILABLE_TIME", "last_year"))

        print first_year, last_year

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
        return User(user_login="WHOIMPORTER")

    def _build_default_datasource(self):
        result = DataSource(chain_for_id=self._org_id, int_for_id=self._sou_int)
        self._sou_int += 1  # Update
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
        result.description = self._config.get("ORGANIZATION", "description")

        return result


    def _build_default_license(self):
        # TODO: Revise ALL this data. There is not clear license
        result = License()
        result.republish = self._config.get("LICENSE", "republish")
        result.description = self._config.get("LICENSE", "description")
        result.name = self._config.get("LICENSE", "name")
        result.url = self._config.get("LICENSE", "url")

        return result

    def _build_indicators_dict(self):
        result = {}
        
        #Gross National Income
        gni_ind = Indicator(chain_for_id=self._org_id,
                                     int_for_id=self._ind_int)
        self._ind_int += 1  # Updating id value
        gni_ind.name_en = self._read_config_value("INDICATOR", "gni_name_en")
        gni_ind.name_es = self._read_config_value("INDICATOR", "gni_name_es")
        gni_ind.name_fr = self._read_config_value("INDICATOR", "gni_name_fr")
        gni_ind.description_en = self._read_config_value("INDICATOR", "gni_desc_en")
        gni_ind.description_es = self._read_config_value("INDICATOR", "gni_desc_es")
        gni_ind.description_fr = self._read_config_value("INDICATOR", "gni_desc_fr")
        gni_ind.measurement_unit = MeasurementUnit("units")
        gni_ind.topic = Indicator.TOPIC_TEMPORAL
        gni_ind.preferable_tendency = Indicator.IRRELEVANT  # TODO: No idea

        result[self.GNI] = gni_ind

        #Returning final dict
        return result

    def _build_indicators_endpoint(self):
        result = {}
        
        gni_ind_end = IndicatorEndpoint()
        gni_ind_end.code = self._read_config_value("INDICATOR", "gni_code_value")
        gni_ind_end.profile = self._read_config_value("INDICATOR", "gni_profile_value")
        gni_ind_end.countries = self._read_config_value("INDICATOR", "gni_countries_value")
        gni_ind_end.regions = self._read_config_value("INDICATOR", "gni_regions_value")
        gni_ind_end.file_name = self._read_config_value("INDICATOR", "gni_file_name")
        
        result[self.GNI] = gni_ind_end
        
        return result;
        

    def _read_config_value(self, section, field):
        return (self._config.get(section, field)).decode(encoding="utf-8")


    def _relate_common_objects(self):
        self._default_organization.add_user(self._default_user)
        self._default_organization.add_data_source(self._default_datasource)
        self._default_datasource.add_dataset(self._default_dataset)
        self._default_dataset.license_type = self._default_license
        #No return needed
