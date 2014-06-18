from datetime import datetime
import os

from lpentities.computation import Computation
from lpentities.data_source import DataSource
from lpentities.dataset import Dataset
from lpentities.indicator import Indicator
from lpentities.instant import Instant
from lpentities.interval import Interval
from lpentities.license import License
from lpentities.measurement_unit import MeasurementUnit
from lpentities.observation import Observation
from lpentities.organization import Organization
from lpentities.user import User
from lpentities.value import Value
from lpentities.year_interval import YearInterval
from model2xml.model2xml import ModelToXMLTransformer
from reconciler.country_reconciler import CountryReconciler

from es.weso.transint.ExcelManagement.excel_reader import XslReader


__author__ = 'BorjaGB'

class TransIntImporter(object):

    def __init__(self, log, config, look_for_historical):
        self._log = log
        self._config = config
        self._look_for_historical = look_for_historical
        if not look_for_historical:
            self._historical_year = self._config.getint("TRANSLATOR", "historical_year")
            self._obs_int = self._config.getint("TRANSLATOR", "obs_int")
            self._sli_int = self._config.getint("TRANSLATOR", "sli_int")
            self._dat_int = self._config.getint("TRANSLATOR", "dat_int")
            self._igr_int = self._config.getint("TRANSLATOR", "igr_int")
        else:
            self._obs_int = 0
            self._sli_int = 0
            self._dat_int = 0
            self._igr_int = 0

        self._reconciler = CountryReconciler()

        self._org_id = self._config.get("TRANSLATOR", "org_id")


        self.data_sources = dict(self._config.items('indicators'))

        # Building parsing instances
        self._xsl_reader = self._build_xsl_reader()
        
        # Building common objects
        self._default_user = self._build_default_user()  # Done
        self._default_datasource = self._build_default_datasource()  # Done
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
        # Download csv file for specified indicators in config file
        
        # Generate observations and add it to the common objects
        self._load_xsls()
        
        # And it is done. No return needed

    def _build_xsl_reader(self):
        return XslReader()
    
    def _actualize_config_values(self, last_year):
        self._config.set("TRANSLATOR", "org_id", self._org_id)
        self._config.set("TRANSLATOR", "obs_int", self._obs_int)
        self._config.set("TRANSLATOR", "sli_int", self._sli_int)
        self._config.set("TRANSLATOR", "dat_int", self._dat_int)
        self._config.set("TRANSLATOR", "igr_int", self._igr_int)


    def _load_xsls(self):
        self._log.info("Reading files...")
        
        for data_source_name in self.data_sources:
            dataset = self._build_dataset()

            indicators_section = self._config.get('indicators', data_source_name)
            indicator_element = dict(self._config.items(indicators_section))
            
            indicator = self._build_indicator(indicator_element)
            
            file_names = indicator_element['file'].split(',')
            for file_name in file_names:
                result=[]
                data = self._xsl_reader.load_xsl(indicator_element, file_name)
                if file_name.startswith('open_budget'):
                    result+=self._extract_observations_obi(indicator, data)
                elif file_name.startswith('worldwide'):
                    result+=self._extract_observations_wgi(indicator, data)
                else:
                    result+=self._extract_observations_cpi(indicator, data, file_name.split('-')[0])
                
                path_to_file = os.path.join(self._xsl_reader._data_path, os.path.basename(file_name))
                
                if len(result) > 0:
                    for obs in result:
                        dataset.add_observation(obs)
                    # Send model for its translation
                    translator = ModelToXMLTransformer(dataset=dataset, import_process=ModelToXMLTransformer.XLS, user=self._default_user, path_to_original_file=path_to_file)
                    translator.run()
                else:
                    self._log.warning("No observations found for dataset " + file_name)
            
                self._log.info("Done with Excel file %s" % (file_name))
        
    def _extract_observations_obi(self, indicator, data):
        observations = []
        country_col = 0
        year_col = 1
        index_col = 2
        
        country = None
        for row in data:
            if country is None or country.iso2 != row[country_col]:
                country = self._get_country(row[country_col])
            year = self._build_ref_time_object(row[year_col])
            if self._filter_historical_observations(year):
                value = self._build_value_object(row[index_col], Value.INTEGER)
                observations.append(self._build_observation_for_cell(indicator, year, value, country))
                
        return observations
    
    def _extract_observations_wgi(self, indicator, data):
        observations = []
        years_row = 0
        indicators_row = 1
        
        country_col = 0
        
        available_columns = []
        for i, cell in enumerate(data[indicators_row]):
            if cell == 'P-Rank' or cell == 'Rank':
                available_columns.append(i)
                
        country = None
        for row in data:
            country = self._get_country(row[country_col])
            if country is not None:
                for col in available_columns:
                    year = self._build_ref_time_object(data[years_row][col])
                    if self._filter_historical_observations(year):
                        value = self._build_value_object(row[col], Value.FLOAT)
                        observations.append(self._build_observation_for_cell(indicator, year, value, country))
                
        return observations
    
    def _extract_observations_cpi(self, indicator, data, year):
        observations = []
        country_col = 1
        index_col = 5
        
        country = None
        year = self._build_ref_time_object(year)
        
        if self._filter_historical_observations(year):
            for row in data:
                country = self._get_country(row[country_col])
                
                if country is not None:
                    value = self._build_value_object(row[index_col], Value.INTEGER)
                    observations.append(self._build_observation_for_cell(indicator, year, value, country))
                    
        return observations
    
    def _filter_historical_observations(self, year): 
        if self._look_for_historical:
            return True
        else :
            if isinstance(year, YearInterval):
                return year.year > self._historical_year
            else:
                return year.end_time > self._historical_year 
    
    def _extract_data_from_matrix(self, file_name, data):
        result = []
        
        return result
        
    def _build_observation_for_cell(self, indicator, year, value, country):
        result = Observation(chain_for_id=self._org_id, int_for_id=self._obs_int)
        self._obs_int += 1  # Updating id value
        
        result.indicator = indicator
        result.value = value
        result.computation = self._get_computation_object()  # Always the same, no param needed
        result.issued = self._build_issued_object()  # No param needed
        result.ref_time = year
        country.add_observation(result)  # And that stablish the relation in both directions
        
        return result
    
    @staticmethod
    def _build_ref_time_object(year):
        years = str(year).split("-")
        if len(years) == 1:
            if len(str(year)) == 2:
                return YearInterval(year=int("19" + str(year)))
            return YearInterval(year=int(float(year)))
        else :
            if len(years[1]) == 2:
                if years[1].startswith('0') and years[0].startswith('19'): 
                    return Interval(start_time=int(years[0]), end_time=int("20"+years[1]))
                else :
                    return Interval(start_time=int(years[0]), end_time=int(years[0][:2]+years[1]))
            else :
                return Interval(start_time=int(years[0]), end_time=int(years[1]))

    def _build_issued_object(self):
        return Instant(datetime.now())

    def _get_computation_object(self):
        return self._default_computation

    @staticmethod
    def _build_value_object(value, value_type):
        try:
            if not (value is None or value == "" or value == '{#N/D}'):
                if (value_type == Value.INTEGER):
                    int(value)
                elif  (value_type == Value.FLOAT):
                    if value == "<5":
                        value = "4"
                    float(value)
                return Value(value=value,
                             value_type=value_type,
                             obs_status=Value.AVAILABLE)
            else:
                return Value(value=None,
                             value_type=value_type,
                             obs_status=Value.MISSING)
        except:
            return Value(value=None,
                         value_type=value_type,
                         obs_status=Value.MISSING)
        
    def _get_country(self, identificator):
        country = None
        try:
            country = self._reconciler.get_country_by_iso3(identificator)
        except:
            try:
                country = self._reconciler.get_country_by_iso2(identificator)
            except:
                try: 
                    country = self._reconciler.get_country_by_en_name(identificator)
                except:
                    try:
                        country = self._reconciler.get_country_by_es_name(identificator)
                    except:
                        try:
                            country = self._reconciler.get_country_by_fr_name(identificator)
                        except:
                            country = None
        
        return country

    def _build_default_user(self):
        return User(user_login="TRANSINTIMPORTER")

    def _build_default_datasource(self):
        result = DataSource(chain_for_id=self._org_id,
                            int_for_id=int(self._config.get("DATASOURCE", "datasource_id")))
        result.name = self._config.get("DATASOURCE", "name")
        return result

    def _build_dataset(self):
        result = Dataset(chain_for_id=self._org_id, int_for_id=self._dat_int)
        self._dat_int += 1  # Needed increment
        result.frequency = Dataset.YEARLY
        
        self._default_datasource.add_dataset(result)
        result.license_type = self._default_license

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

    def _build_indicator(self, indicator_dict):
        measurement_unit = MeasurementUnit(name=indicator_dict['indicator_unit_name'], 
                                           convert_to=indicator_dict['indicator_unit_type'])
        
        indicator = Indicator(chain_for_id=self._org_id,
                          int_for_id=int(indicator_dict['indicator_id']),
                          name_en=indicator_dict['name_en'].decode("UTF-8"),
                          name_es=indicator_dict['name_es'].decode("UTF-8"),
                          name_fr=indicator_dict['name_fr'].decode("UTF-8"), 
                          description_en=indicator_dict['desc_en'].decode("UTF-8"),
                          description_es=indicator_dict['desc_es'].decode("UTF-8"),
                          description_fr=indicator_dict['desc_fr'].decode("UTF-8"),
                          measurement_unit= measurement_unit,
                          preferable_tendency=self._get_preferable_tendency_of_indicator(indicator_dict['indicator_tendency']),
                          topic=indicator_dict['indicator_topic'])
    
        return indicator

    @staticmethod
    def _get_preferable_tendency_of_indicator(tendency):
        if tendency.lower() == "decrease":
            return Indicator.DECREASE
        else:
            return Indicator.INCREASE
        
    def _read_config_value(self, section, field):
        return (self._config.get(section, field)).decode(encoding="utf-8")


    def _relate_common_objects(self):
        self._default_organization.add_user(self._default_user)
        self._default_organization.add_data_source(self._default_datasource)
