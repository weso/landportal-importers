from datetime import datetime
import os

from lpentities.computation import Computation
from lpentities.data_source import DataSource
from lpentities.dataset import Dataset
from lpentities.indicator import Indicator
from lpentities.instant import Instant
from lpentities.license import License
from lpentities.measurement_unit import MeasurementUnit
from lpentities.observation import Observation
from lpentities.organization import Organization
from lpentities.user import User
from lpentities.value import Value
from lpentities.year_interval import YearInterval
from model2xml.model2xml import ModelToXMLTransformer
from reconciler.country_reconciler import CountryReconciler

from data import __data__
from es.weso.who.importers.data_management.csv_downloader import CsvDownloader
from es.weso.who.importers.data_management.csv_reader import CsvReader
from es.weso.who.importers.data_management.indicator_endpoint import IndicatorEndpoint


__author__ = 'BorjaGB'

class WhoImporter(object):

    def __init__(self, log, config, look_for_historical):
        self._log = log
        self._config = config
        self._look_for_historical = look_for_historical
        
        if not self._look_for_historical:
            self._historical_year = self._config.getint("TRANSLATOR", "historical_year")
            self._last_year = self._historical_year
            # Initializing variable ids, as is not historical mode, we use the values that we already have
            self._org_id = self._config.get("TRANSLATOR", "org_id")
            self._obs_int = self._config.getint("TRANSLATOR", "obs_int")
            self._sli_int = self._config.getint("TRANSLATOR", "sli_int")
            self._dat_int = self._config.getint("TRANSLATOR", "dat_int")
            self._igr_int = self._config.getint("TRANSLATOR", "igr_int")
        else :
            # Initializing variable ids, as is historical mode, everything is empty data
            self._org_id = self._config.get("TRANSLATOR", "org_id")
            self._obs_int = 0
            self._sli_int = 0
            self._dat_int = 0
            self._igr_int = 0
            self._last_year = 0
        
        self._reconciler = CountryReconciler()

        # Indicators_dict
        self._indicators_dict = self._build_indicators_dict()
        self._indicators_endpoints = self._build_indicators_endpoint()
        
        # Building parsing instances
        self._csv_downloader = self._build_csv_downloader()
        self._csv_reader = self._build_csv_reader()
        
        # Building common objects
        self._default_user = self._build_default_user()  # Done
        self._default_datasource = self._build_default_datasource()  # Done
        self._default_dataset = self._build_default_dataset()  # Done
        self._default_organization = self._build_default_organization()  # Done
        self._default_license = self._build_default_license()  # Done
        self._relate_common_objects()  # Done
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
        self._file_paths = []
        # Download csv file for specified indicators in config file
        self._download_csvs()
        
        # Generate observations and add it to the common objects
        observations = self._build_observations()
        if len(observations) > 0:
            for obs in observations :
                self._default_dataset.add_observation(obs)
                    
            # Send model for its trasnlation
            translator = ModelToXMLTransformer(dataset=self._default_dataset, import_process=ModelToXMLTransformer.CSV,
                                               user=self._default_user,
                                               path_to_original_file=self._file_paths)
            translator.run()
            
        else:
            self._log.warn("No observations found")
        # And it is done. No return needed

    def _build_csv_downloader(self):
        return CsvDownloader(url_pattern=self._config.get("IMPORTER", "url_pattern"),
                              indicator_pattern=self._config.get("IMPORTER", "indicator_pattern"),
                              profile_pattern=self._config.get("IMPORTER", "profile_pattern"),
                              countries_pattern=self._config.get("IMPORTER", "countries_pattern"),
                              region_pattern=self._config.get("IMPORTER", "region_pattern"))
    
    def _build_csv_reader(self):
        return CsvReader()
    
    def _download_csvs(self):
        self._log.info("Downloading csv files...")
        for ind_end in self._indicators_endpoints:
            self._file_paths.append(os.path.join(__data__.path(), os.path.basename(self._indicators_endpoints[ind_end].file_name)))
            
            if self._csv_downloader.download_csv(self._indicators_endpoints[ind_end].indicator_code, self._indicators_endpoints[ind_end].profile, self._indicators_endpoints[ind_end].countries, self._indicators_endpoints[ind_end].regions, self._indicators_endpoints[ind_end].file_name) :
                self._log.info("\tSUCCESS downloading: " + self._indicators_endpoints[ind_end].file_name)
            else:
                self._log.error("\tERROR downloading: " + self._indicators_endpoints[ind_end].file_name + " probably the file was already downloaded and processed")

    def _build_observations(self):
        observations = []
        
        for ind_end in self._indicators_endpoints:
            csv_headers, csv_content = self._csv_reader.load_csv(self._indicators_endpoints[ind_end].file_name)
            observations += self._build_observations_for_file(csv_headers, csv_content)
        
        return observations
          
    def _filter_historical_observations(self, year): 
        # Update year value for historical
        if isinstance(year, YearInterval):
            if year.year > self._last_year:
                self._last_year = year.year
        elif year.end_time > self._last_year:
                self._last_year = year.end_time
                    
        if self._look_for_historical:  
            return True
        else :
            if isinstance(year, YearInterval):
                return year.year > self._historical_year
            else:
                return year.end_time > self._historical_year
   
    def _build_observations_for_file(self, file_headers, file_content):
        observations = []
        
        indicator_index = file_headers.index('GHO (CODE)')
        year_index = file_headers.index('YEAR (CODE)')
        value_index = file_headers.index('Numeric')
        country_index = file_headers.index('COUNTRY (CODE)')
        
        for row in file_content:
            year = self._build_ref_time_object(row[year_index])
            
            if self._filter_historical_observations(year):
                observations.append(self._build_observation_for_line(row, indicator_index, year, value_index, country_index))
        
        return observations
            
    def _build_observation_for_line(self, row, indicator_index, year, value_index, country_index):
        result = Observation(chain_for_id=self._org_id, int_for_id=self._obs_int)
        self._obs_int += 1  # Updating id value
        
        result.indicator = self._indicators_dict[row[indicator_index]]
        result.value = self._build_value_object(row[value_index])
        result.computation = self._get_computation_object()  # Always the same, no param needed
        result.issued = self._build_issued_object()  # No param needed
        result.ref_time = year
        self._get_country_by_iso3(row[country_index]).add_observation(result)  # And that stablish therelation in both directions
        
        return result
    
    @staticmethod
    def _build_ref_time_object(year):
        return YearInterval(year=int(year))

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

    def _get_country_by_iso3(self, country_iso):
        return self._reconciler.get_country_by_iso3(country_iso)

    def _build_default_user(self):
        return User(user_login="WHOIMPORTER")

    def _build_default_datasource(self):
        result = DataSource(chain_for_id=self._org_id,
                            int_for_id=int(self._read_config_value("DATASOURCE", "datasource_id")))
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
        requested_indicators = dict(self._config.items("INDICATORS"))
        
        for indicator_element in requested_indicators:
            indicator_code = self._config.get("INDICATORS", indicator_element)
            indicator_object = Indicator(chain_for_id=self._org_id,
                                         int_for_id=self._config.get(indicator_code, "indicator_id"))
            indicator_object.name_en = self._read_config_value(indicator_code, "name_en")
            indicator_object.name_es = self._read_config_value(indicator_code, "name_es")
            indicator_object.name_fr = self._read_config_value(indicator_code, "name_fr")
            indicator_object.description_en = self._read_config_value(indicator_code, "desc_en")
            indicator_object.description_es = self._read_config_value(indicator_code, "desc_es")
            indicator_object.description_fr = self._read_config_value(indicator_code, "desc_fr")
            indicator_object.measurement_unit = MeasurementUnit(name=self._read_config_value(indicator_code, "indicator_unit_name"),
                                                                convert_to=self._read_config_value(indicator_code, "indicator_unit_type"))
            indicator_object.topic = self._read_config_value(indicator_code, "indicator_topic")
            indicator_object.preferable_tendency = self._parse_preferable_tendency(self._read_config_value(indicator_code, "indicator_tendency"))
    
            result[indicator_code] = indicator_object
    
            # Returning final dict
        return result

    def _parse_preferable_tendency(self, tendency):
        if tendency.lower() == "increase":
            return Indicator.INCREASE
        elif tendency.lower() == "decrease":
            return Indicator.DECREASE
        return Indicator.IRRELEVANT

    def _build_indicators_endpoint(self):
        result = {}
        requested_indicators = dict(self._config.items("INDICATORS"))
        
        for indicator_element in requested_indicators:
            indicator_code = self._config.get("INDICATORS", indicator_element)
            indicator_endpoint = IndicatorEndpoint()
            indicator_endpoint.indicator_code = "GHO/" + indicator_code
            indicator_endpoint.profile = self._read_config_value(indicator_code, "profile_value")
            indicator_endpoint.countries = self._read_config_value(indicator_code, "countries_value")
            indicator_endpoint.regions = self._read_config_value(indicator_code, "regions_value")
            indicator_endpoint.file_name = self._read_config_value(indicator_code, "file_name")
            
            result[indicator_code] = indicator_endpoint
        
        return result;
        

    def _read_config_value(self, section, field):
        return (self._config.get(section, field)).decode(encoding="utf-8")


    def _relate_common_objects(self):
        self._default_organization.add_user(self._default_user)
        self._default_organization.add_data_source(self._default_datasource)
        self._default_datasource.add_dataset(self._default_dataset)
        self._default_dataset.license_type = self._default_license
        # No return needed
