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

from es.weso.fao.ExcelManagement.excel_reader import XslReader


__author__ = 'BorjaGB'


class FaoImporter(object):

    def __init__(self, log, config, look_for_historical):
        self._log = log
        self._config = config
        self._look_for_historical = look_for_historical
        self._org_id = self._config.get("TRANSLATOR", "org_id")
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

        # Initializing variable ids



        self.data_sources = dict(self._config.items('data_sources'))
        
        # Indicators_dict
        self._indicators_dict = self._build_indicators_dict()
        
        # Building parsing instances
        self._xsl_reader = self._build_xsl_reader()
        
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
        # Download csv file for specified indicators in config file
        
        # Generate observations and add it to the common objects
        observations = self._load_xsls()
        if len(observations) > 0:
            for obs in observations :
                self._default_dataset.add_observation(obs)
        else:
            self._log.warning("No observations found")
            
        # Send model for its trasnlation
        translator = ModelToXMLTransformer(dataset=self._default_dataset, 
                                           import_process=ModelToXMLTransformer.XLS, 
                                           user=self._default_user,
                                           path_to_original_file=os.path.join(self._xsl_reader._data_path, os.path.basename(self._config.get("PARSER", "file_name"))))
        translator.run()

        # And it is done. No return needed

    def _build_xsl_reader(self):
        return XslReader()
    
    def _actualize_config_values(self, last_year):
        self._config.set("TRANSLATOR", "org_id", self._org_id)
        self._config.set("TRANSLATOR", "obs_int", self._obs_int)
        self._config.set("TRANSLATOR", "sli_int", self._sli_int)
        self._config.set("TRANSLATOR", "dat_int", self._dat_int)
        self._config.set("TRANSLATOR", "igr_int", self._igr_int)
        self._config.set("TRANSLATOR", "ind_int", self._ind_int)
        self._config.set("TRANSLATOR", "sou_int", self._sou_int)

    def _load_xsls(self):
        result = []
        self._log.info("Reading files...")
        file_name = self._config.get("PARSER", "file_name")
        years_row = int(self._config.get("PARSER", "year_row"))-1
        
        for data_source_name in self.data_sources:
            indicators_section = self._config.get('data_sources', data_source_name)
            requested_indicators = dict(self._config.items(indicators_section))
            
            for indicator_element in requested_indicators:
                indicator_code = self._config.get(indicators_section, indicator_element)
                index = int(self._config.get(indicator_code, "indicator_id"))
                indicator_sheet = self._config.get(indicator_code, "excel_sheet")
                data = self._xsl_reader.load_xsl(file_name, indicator_sheet)
                
                for i in range(4, len(data)):
                    country = self._get_country_by_name(data[i][1])
                    if country is not None :
                        for j in range(2, len(data[years_row])):
                            
                            year = self._build_ref_time_object(data[years_row][j])
                            if self._filter_historical_observations(year):
                                value = self._build_value_object(data[i][j], Value.FLOAT)
                                result.append(self._build_observation_for_cell(index,
                                                                               year,
                                                                               value,
                                                                               country))
        self._log.info("Done with Excel file %s" % (file_name))
        
        return result
    
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
        
    def _build_observation_for_cell(self, indicator_index, year, value, country):
        result = Observation(chain_for_id=self._org_id, int_for_id=self._obs_int)
        self._obs_int += 1  # Updating id value
        
        result.indicator = self._indicators_dict[indicator_index]
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
            if not (value is None or value == ""):
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
        
    def _get_country_by_name(self, country_name):
        country = None
        try: 
            country = self._reconciler.get_country_by_en_name(country_name)
        except:
            try:
                country = self._reconciler.get_country_by_es_name(country_name)
            except:
                try:
                    country = self._reconciler.get_country_by_fr_name(country_name)
                except:
                    country = None
        
        return country

    def _build_default_user(self):
        return User(user_login="FAOIMPORTER")

    def _build_default_datasource(self):
        result = DataSource(chain_for_id=self._org_id,
                            int_for_id=int(self._config.get("DATASOURCE", "datasource_id")))
        result.name = self._config.get("DATASOURCE", "name")
        return result

    def _build_default_dataset(self):
        result = Dataset(chain_for_id=self._org_id, int_for_id=self._dat_int)
        self._dat_int += 1  # Needed increment
        result.frequency = Dataset.YEARLY
        return result

    def _build_default_organization(self):
        result = Organization(chain_for_id=self._config.get("ORGANIZATION", "chain_for_id"))
        result.name = self._config.get("ORGANIZATION", "name")
        result.url = self._config.get("ORGANIZATION", "url")
        result.url_logo = self._config.get("ORGANIZATION", "url_logo")
        result.description_en = self._read_config_value("ORGANIZATION", "description_en")
        result.description_es = self._read_config_value("ORGANIZATION", "description_es")
        result.description_fr = self._read_config_value("ORGANIZATION", "description_fr")

        return result

    def _read_config_value(self, section, field):
        return (self._config.get(section, field)).decode(encoding="utf-8")


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
        for data_source_name in self.data_sources:
            indicators_section = self._config.get('data_sources', data_source_name)
            requested_indicators = dict(self._config.items(indicators_section))
            
            for indicator_element in requested_indicators:
                indicator_code = self._config.get(indicators_section, indicator_element)
                #print "%s, %d" %(indicator_code,self._ind_int) 
                result[int(self._config.get(indicator_code, "indicator_id"))] = self._build_indicator(indicator_code)
                
        # Returning final dict
        return result

    def _build_indicator(self, indicator_code):
        indicator = Indicator(chain_for_id=self._org_id,
                          int_for_id=int(self._config.get(indicator_code, "indicator_id")),
                          name_en=self._config.get(indicator_code, "name_en").decode(encoding="utf-8"),
                          name_es=self._config.get(indicator_code, "name_es").decode(encoding="utf-8"),
                          name_fr=self._config.get(indicator_code, "name_fr").decode(encoding="utf-8"), 
                          description_en=self._config.get(indicator_code, "desc_en").decode(encoding="utf-8"),
                          description_es=self._config.get(indicator_code, "desc_es").decode(encoding="utf-8"),
                          description_fr=self._config.get(indicator_code, "desc_fr").decode(encoding="utf-8"),
                          measurement_unit= MeasurementUnit(name= self._config.get(indicator_code, "indicator_unit_name"),
                                                            convert_to = self._config.get(indicator_code, "indicator_unit_type")),
                          preferable_tendency=self._get_preferable_tendency_of_indicator(self._config.get(indicator_code, "indicator_tendency")),
                          topic=self._config.get(indicator_code, "indicator_topic"))  # TODO: temporal value
    
        return indicator

    @staticmethod
    def _get_preferable_tendency_of_indicator(tendency):
        if tendency.lower() == "decrease":
            return Indicator.DECREASE
        else:
            return Indicator.INCREASE

    def _relate_common_objects(self):
        self._default_organization.add_user(self._default_user)
        self._default_organization.add_data_source(self._default_datasource)
        self._default_datasource.add_dataset(self._default_dataset)
        self._default_dataset.license_type = self._default_license
        # No return needed
