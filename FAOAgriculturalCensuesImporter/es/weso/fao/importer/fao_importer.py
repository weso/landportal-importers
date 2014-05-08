from datetime import datetime

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

from es.weso.fao.ExcelManagement.excel_reader import XslReader
from lpentities.interval import Interval


__author__ = 'BorjaGB'

class FaoImporter(object):

    def __init__(self, log, config, look_for_historical):
        self._log = log
        self._config = config
        self._look_for_historical = look_for_historical
        if not self._look_for_historical:
            self._historical_year = self._config.getint("TRANSLATOR", "historical_year")
        self._reconciler = CountryReconciler()

        # Initializing variable ids
        self._org_id = self._config.get("TRANSLATOR", "org_id")
        self._obs_int = self._config.getint("TRANSLATOR", "obs_int")
        self._sli_int = self._config.getint("TRANSLATOR", "sli_int")
        self._dat_int = self._config.getint("TRANSLATOR", "dat_int")
        self._igr_int = self._config.getint("TRANSLATOR", "igr_int")

        # Indicators code
        self.TNH = 0  # Total number of holdings
        self.TAH = 1  # Total areas holding
        self.NOW = 2  # Number operated as owner
        self.NTE = 3  # Number operated as tenant
        self.NOT = 4  # Number operated as others
        self.AOW = 5  # Areas operated as owner
        self.ATE = 6  # Areas operated as tenant
        self.AOT = 7  # Areas operated as others
        self.SNOW = 8  # Shares in number operated as owner
        self.SNTE = 9  # Shares in number operated as tenant
        self.SNOT = 10  # Shares in number operated as others
        self.SAOW = 11  # Shares in areas operated as owner
        self.SATE = 12  # Shares in areas operated as tenant
        self.SAOT = 13  # Shares in areas operated as others
        self.NMO = 14  # Number in more than one form of tenure
        self.SNMO = 15  # Shares in number under more than one for of tenure
        self.AMO = 16  # Areas in more than one form of tenure
        self.SAMO = 17  # Shares is areas operated in more than one form of tenure
        
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
        if len(observations > 0):
            for obs in observations :
                self._default_dataset.add_observation(obs)
                    
            # Send model for its trasnlation
            translator = ModelToXMLTransformer(self._default_dataset, "API_REST", self._default_user)
            translator.run()
        else:
            print "No observations found"
            
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
        self._config.set("AVAILABLE_TIME", "last_checked_year", last_year)

    def _load_xsls(self):
        result = []
        print "Reading files..."
        for file_name in self._config.get("PARSER", "file_names").split(","):
            rows_range = self._config.get("PARSER", "data_range_rows_" + file_name.strip()).split("-")
            cols_range = self._config.get("PARSER", "data_range_cols_" + file_name.strip()).split("-")
            data = self._xsl_reader.load_xsl(file_name.strip(), rows_range, cols_range)
            result += self._extract_data_from_matrix(file_name.strip(), data)
            print "Done with Excel file %s" % (file_name)
            
        return result
    
    def _extract_data_from_matrix(self, file_name, data):
        result = []
        
        if file_name == "Land_operated_by_tenure_type 2000.xls":
            result += self._extract_data_operated_tenure_type(data)
        elif file_name == "Land_tenure 2000.xls":
            result +=self._extract_data_land_tenure_2000(data)
        elif file_name == "Land tenure_1970.1980.1990.xlsx":
            result +=self._extract_data_land_tenure_old(data)
        
        return result
    
    def _filter_historical_observations(self, year): 
        if self._look_for_historical:
            return True
        else :
            if isinstance(year, YearInterval):
                return year.year > self._historical_year
            else:
                return year.end_time > self._historical_year 
 
    def _extract_data_generic(self, data, country_col, year_col, tnh_col = None, tah_col = None, 
                              now_col = None, nte_col = None, not_col = None, nmo_col = None, 
                              aow_col = None, ate_col = None, aot_col = None, amo_col = None):
        result = []
        
        country = None
        for i, element in enumerate(data):  # i is used so the enumerate doesn't show the index as first column
            if element[year_col] != "" :
                if element[country_col] != "":
                    country = self._get_country_by_name(element[country_col])
                year = self._build_ref_time_object(str(element[year_col]).replace("/", "-"))
                
                if self._filter_historical_observations(year):
                    if (tnh_col != None):
                        tnh_result = self._build_observation_for_line(self.TNH, year, element[tnh_col], Value.INTEGER, country)
                        result.append(tnh_result)        
                    if (tah_col != None):
                        tah_result = self._build_observation_for_line(self.TAH, year, element[tah_col], Value.INTEGER, country)
                        result.append(tah_result)
                    if (now_col != None):
                        now_result = self._build_observation_for_line(self.NOW, year, element[now_col], Value.INTEGER, country)
                        result.append(now_result)
                    if (aow_col != None):
                        aow_result = self._build_observation_for_line(self.AOW, year, element[aow_col], Value.INTEGER, country)
                        result.append(aow_result)
                    if (nte_col != None):
                        nte_result = self._build_observation_for_line(self.NTE, year, element[nte_col], Value.INTEGER, country)
                        result.append(nte_result)
                    if (ate_col != None):
                        ate_result = self._build_observation_for_line(self.ATE, year, element[ate_col], Value.INTEGER, country)
                        result.append(ate_result)
                    if (not_col != None):
                        not_result = self._build_observation_for_line(self.NOT, year, element[not_col], Value.INTEGER, country)
                        result.append(not_result)
                    if (aot_col != None):
                        aot_result = self._build_observation_for_line(self.AOT, year, element[aot_col], Value.INTEGER, country)
                        result.append(aot_result)
                    if (nmo_col != None):
                        nmo_result = self._build_observation_for_line(self.NMO, year, element[nmo_col], Value.INTEGER, country)
                        result.append(nmo_result)
                    if (amo_col != None):
                        amo_result = self._build_observation_for_line(self.AMO, year, element[amo_col], Value.INTEGER, country)
                        result.append(amo_result)
                    
                    if (tnh_col != None):
                        if (now_col != None):
                            result.append(self._build_observation_for_line(self.SNOW, year, self._calculate_percentage_of_data(tnh_result.value.value, now_result.value.value), Value.FLOAT, country))
                        if (nte_col != None):
                            result.append(self._build_observation_for_line(self.SNTE, year, self._calculate_percentage_of_data(tnh_result.value.value, nte_result.value.value), Value.FLOAT, country))
                        if (not_col != None):
                            result.append(self._build_observation_for_line(self.SNOT, year, self._calculate_percentage_of_data(tnh_result.value.value, not_result.value.value), Value.FLOAT, country))
                        if (nmo_col != None):
                            result.append(self._build_observation_for_line(self.SNMO, year, self._calculate_percentage_of_data(tnh_result.value.value, nmo_result.value.value), Value.FLOAT, country))
                            
                    if (tah_col != None):                        
                        if (aow_col != None):
                            result.append(self._build_observation_for_line(self.SAOW, year, self._calculate_percentage_of_data(tah_result.value.value, aow_result.value.value), Value.FLOAT, country))
                        if (ate_col != None):
                            result.append(self._build_observation_for_line(self.SATE, year, self._calculate_percentage_of_data(tah_result.value.value, ate_result.value.value), Value.FLOAT, country))
                        if (aot_col != None):
                            result.append(self._build_observation_for_line(self.SAOT, year, self._calculate_percentage_of_data(tah_result.value.value, aot_result.value.value), Value.FLOAT, country))
                        if (amo_col != None):
                            result.append(self._build_observation_for_line(self.SAMO, year, self._calculate_percentage_of_data(tah_result.value.value, amo_result.value.value), Value.FLOAT, country))
                        
        return result
        
    def _extract_data_operated_tenure_type(self, data):
        return self._extract_data_generic(data, country_col = 0, year_col = 1, 
                                          tah_col = 2, aow_col = 4, ate_col = 5, aot_col = 6)
     
    
    def _extract_data_land_tenure_2000(self, data):
        return self._extract_data_generic(data, country_col = 0, year_col = 1, tnh_col = 2, tah_col = 4, 
                                          now_col = 5, nte_col = 9, not_col = 13, nmo_col = 17,
                                          aow_col = 7, ate_col = 11, aot_col = 15, amo_col = 19)
        
    def _extract_data_land_tenure_old(self, data):
        return self._extract_data_generic(data, country_col = 0, year_col = 1, tnh_col = 2, tah_col = 3,
                                          now_col = 4, nte_col = 6, not_col = 8, nmo_col = 10, 
                                          aow_col = 5, ate_col = 7, aot_col = 9, amo_col = 11)
        
    def _calculate_percentage_of_data(self, total_number, partial_number):
        if (total_number == None or partial_number == None) :
            return None
        else:
            return (float(partial_number)/float(total_number)) * 100
        
    def _build_observation_for_line(self, indicator_index, year, value, value_type, country):
        result = Observation(chain_for_id=self._org_id, int_for_id=self._obs_int)
        self._obs_int += 1  # Updating id value
        
        result.indicator = self._indicators_dict[indicator_index]
        result.value = self._build_value_object(value, value_type)
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
            if len(years[0]) == 2:
                return Interval(start_time=int("19"+years[0]), end_time=int("19"+years[1]))
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
                country = self._reconciler.get_country_by_fr_name(country_name)
        
        return country

    def _build_default_user(self):
        return User(user_login="FAOIMPORTER")

    def _build_default_datasource(self):
        result = DataSource(chain_for_id=self._org_id, 
                            int_for_id=self._config.get("DATASOURCE", "datasource_id"))
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
        result = License()
        result.republish = self._config.get("LICENSE", "republish")
        result.description = self._config.get("LICENSE", "description")
        result.name = self._config.get("LICENSE", "name")
        result.url = self._config.get("LICENSE", "url")

        return result

    def _parse_preferable_tendency(self, tendency):
        if tendency.lower() == "increase":
            return Indicator.INCREASE
        elif tendency.lower() == "decrease":
            return Indicator.DECREASE
        return Indicator.IRRELEVANT
    
    def _build_indicators_dict(self):
        result = {}

        number_measure = MeasurementUnit(name = None, convert_to = "units")
        area_measure = MeasurementUnit(name = None, convert_to = "sq. km", factor=10)
        share_measure = MeasurementUnit(name = None, convert_to = "%")
        
        # Total Number of Holdings
        tnh_ind = Indicator(chain_for_id=self._org_id,
                                     int_for_id=self._config.get("INDICATOR", "tnh_id"))
        tnh_ind.name_en = self._read_config_value("INDICATOR", "tnh_name_en")
        tnh_ind.name_es = self._read_config_value("INDICATOR", "tnh_name_es")
        tnh_ind.name_fr = self._read_config_value("INDICATOR", "tnh_name_fr")
        tnh_ind.description_en = self._read_config_value("INDICATOR", "tnh_desc_en")
        tnh_ind.description_es = self._read_config_value("INDICATOR", "tnh_desc_es")
        tnh_ind.description_fr = self._read_config_value("INDICATOR", "tnh_desc_fr")
        number_measure.name = self._read_config_value("INDICATOR", "tnh_unit_name")
        tnh_ind.measurement_unit = number_measure
        tnh_ind.topic = self._read_config_value("INDICATOR", "tnh_topic")
        tnh_ind.preferable_tendency = self._parse_preferable_tendency(
                                                    self._read_config_value("INDICATOR", "tnh_tendency"))

        result[self.TNH] = tnh_ind
                
        # Total Area of Holdings
        tah_ind = Indicator(chain_for_id=self._org_id,
                                     int_for_id=self._config.get("INDICATOR", "tah_id"))
        tah_ind.name_en = self._read_config_value("INDICATOR", "tah_name_en")
        tah_ind.name_es = self._read_config_value("INDICATOR", "tah_name_es")
        tah_ind.name_fr = self._read_config_value("INDICATOR", "tah_name_fr")
        tah_ind.description_en = self._read_config_value("INDICATOR", "tah_desc_en")
        tah_ind.description_es = self._read_config_value("INDICATOR", "tah_desc_es")
        tah_ind.description_fr = self._read_config_value("INDICATOR", "tah_desc_fr")
        area_measure.name = self._read_config_value("INDICATOR", "tah_unit_name")
        tah_ind.measurement_unit = area_measure
        tah_ind.topic = self._read_config_value("INDICATOR", "tah_topic")
        tah_ind.preferable_tendency = self._parse_preferable_tendency(
                                                    self._read_config_value("INDICATOR", "tah_tendency"))
        result[self.TAH] = tah_ind
        
        # Number Operated as Owner
        now_ind = Indicator(chain_for_id=self._org_id,
                                     int_for_id=self._config.get("INDICATOR", "now_id"))
        now_ind.name_en = self._read_config_value("INDICATOR", "now_name_en")
        now_ind.name_es = self._read_config_value("INDICATOR", "now_name_es")
        now_ind.name_fr = self._read_config_value("INDICATOR", "now_name_fr")
        now_ind.description_en = self._read_config_value("INDICATOR", "now_desc_en")
        now_ind.description_es = self._read_config_value("INDICATOR", "now_desc_es")
        now_ind.description_fr = self._read_config_value("INDICATOR", "now_desc_fr")
        number_measure.name = self._read_config_value("INDICATOR", "now_unit_name")
        now_ind.measurement_unit = number_measure
        now_ind.topic = self._read_config_value("INDICATOR", "now_topic")
        now_ind.preferable_tendency = self._parse_preferable_tendency(
                                                    self._read_config_value("INDICATOR", "now_tendency"))
        result[self.NOW] = now_ind
        
        # Number Operated as Tenant
        nte_ind = Indicator(chain_for_id=self._org_id,
                                     int_for_id=self._config.get("INDICATOR", "nte_id"))
        nte_ind.name_en = self._read_config_value("INDICATOR", "nte_name_en")
        nte_ind.name_es = self._read_config_value("INDICATOR", "nte_name_es")
        nte_ind.name_fr = self._read_config_value("INDICATOR", "nte_name_fr")
        nte_ind.description_en = self._read_config_value("INDICATOR", "nte_desc_en")
        nte_ind.description_es = self._read_config_value("INDICATOR", "nte_desc_es")
        nte_ind.description_fr = self._read_config_value("INDICATOR", "nte_desc_fr")
        number_measure.name = self._read_config_value("INDICATOR", "nte_unit_name")
        nte_ind.measurement_unit = number_measure
        nte_ind.topic = self._read_config_value("INDICATOR", "nte_topic")
        nte_ind.preferable_tendency = self._parse_preferable_tendency(
                                                    self._read_config_value("INDICATOR", "nte_tendency"))
        result[self.NTE] = nte_ind

        # Number Operated as Others
        not_ind = Indicator(chain_for_id=self._org_id,
                                     int_for_id=self._config.get("INDICATOR", "not_id"))
        not_ind.name_en = self._read_config_value("INDICATOR", "not_name_en")
        not_ind.name_es = self._read_config_value("INDICATOR", "not_name_es")
        not_ind.name_fr = self._read_config_value("INDICATOR", "not_name_fr")
        not_ind.description_en = self._read_config_value("INDICATOR", "not_desc_en")
        not_ind.description_es = self._read_config_value("INDICATOR", "not_desc_es")
        not_ind.description_fr = self._read_config_value("INDICATOR", "not_desc_fr")
        number_measure.name = self._read_config_value("INDICATOR", "not_unit_name")
        not_ind.measurement_unit = number_measure
        not_ind.topic = self._read_config_value("INDICATOR", "not_topic")
        not_ind.preferable_tendency = self._parse_preferable_tendency(
                                                    self._read_config_value("INDICATOR", "not_tendency"))
        result[self.NOT] = not_ind
        
        # Area Operated as Owner
        aow_ind = Indicator(chain_for_id=self._org_id,
                                     int_for_id=self._config.get("INDICATOR", "aow_id"))
        aow_ind.name_en = self._read_config_value("INDICATOR", "aow_name_en")
        aow_ind.name_es = self._read_config_value("INDICATOR", "aow_name_es")
        aow_ind.name_fr = self._read_config_value("INDICATOR", "aow_name_fr")
        aow_ind.description_en = self._read_config_value("INDICATOR", "aow_desc_en")
        aow_ind.description_es = self._read_config_value("INDICATOR", "aow_desc_es")
        aow_ind.description_fr = self._read_config_value("INDICATOR", "aow_desc_fr")
        area_measure.name = self._read_config_value("INDICATOR", "aow_unit_name")
        aow_ind.measurement_unit = area_measure
        aow_ind.topic = self._read_config_value("INDICATOR", "aow_topic")
        aow_ind.preferable_tendency = self._parse_preferable_tendency(
                                                    self._read_config_value("INDICATOR", "aow_tendency"))
        result[self.AOW] = aow_ind
        
        # Area Operated as Tenant
        ate_ind = Indicator(chain_for_id=self._org_id,
                                     int_for_id=self._config.get("INDICATOR", "ate_id"))
        ate_ind.name_en = self._read_config_value("INDICATOR", "ate_name_en")
        ate_ind.name_es = self._read_config_value("INDICATOR", "ate_name_es")
        ate_ind.name_fr = self._read_config_value("INDICATOR", "ate_name_fr")
        ate_ind.description_en = self._read_config_value("INDICATOR", "ate_desc_en")
        ate_ind.description_es = self._read_config_value("INDICATOR", "ate_desc_es")
        ate_ind.description_fr = self._read_config_value("INDICATOR", "ate_desc_fr")
        area_measure.name = self._read_config_value("INDICATOR", "ate_unit_name")
        ate_ind.measurement_unit = area_measure
        ate_ind.topic = self._read_config_value("INDICATOR", "ate_topic")
        ate_ind.preferable_tendency = self._parse_preferable_tendency(
                                                    self._read_config_value("INDICATOR", "ate_tendency"))
        result[self.ATE] = ate_ind

        # Area Operated as Others
        aot_ind = Indicator(chain_for_id=self._org_id,
                                     int_for_id=self._config.get("INDICATOR", "aot_id"))
        aot_ind.name_en = self._read_config_value("INDICATOR", "aot_name_en")
        aot_ind.name_es = self._read_config_value("INDICATOR", "aot_name_es")
        aot_ind.name_fr = self._read_config_value("INDICATOR", "aot_name_fr")
        aot_ind.description_en = self._read_config_value("INDICATOR", "aot_desc_en")
        aot_ind.description_es = self._read_config_value("INDICATOR", "aot_desc_es")
        aot_ind.description_fr = self._read_config_value("INDICATOR", "aot_desc_fr")
        area_measure.name = self._read_config_value("INDICATOR", "aot_unit_name")
        aot_ind.measurement_unit = area_measure
        aot_ind.topic = self._read_config_value("INDICATOR", "aot_topic")
        aot_ind.preferable_tendency = self._parse_preferable_tendency(
                                                    self._read_config_value("INDICATOR", "aot_tendency"))
        result[self.AOT] = aot_ind

        # Shares in Number Operated as Owner
        snow_ind = Indicator(chain_for_id=self._org_id,
                                     int_for_id=self._config.get("INDICATOR", "snow_id"))
        snow_ind.name_en = self._read_config_value("INDICATOR", "snow_name_en")
        snow_ind.name_es = self._read_config_value("INDICATOR", "snow_name_es")
        snow_ind.name_fr = self._read_config_value("INDICATOR", "snow_name_fr")
        snow_ind.description_en = self._read_config_value("INDICATOR", "snow_desc_en")
        snow_ind.description_es = self._read_config_value("INDICATOR", "snow_desc_es")
        snow_ind.description_fr = self._read_config_value("INDICATOR", "snow_desc_fr")
        share_measure.name = self._read_config_value("INDICATOR", "snow_unit_name")
        snow_ind.measurement_unit = share_measure
        snow_ind.topic = self._read_config_value("INDICATOR", "snow_topic")
        snow_ind.preferable_tendency = self._parse_preferable_tendency(
                                                    self._read_config_value("INDICATOR", "snow_tendency"))
        result[self.SNOW] = snow_ind

        # Shares in Number Operated as Tenant
        snte_ind = Indicator(chain_for_id=self._org_id,
                                     int_for_id=self._config.get("INDICATOR", "snte_id"))
        snte_ind.name_en = self._read_config_value("INDICATOR", "snte_name_en")
        snte_ind.name_es = self._read_config_value("INDICATOR", "snte_name_es")
        snte_ind.name_fr = self._read_config_value("INDICATOR", "snte_name_fr")
        snte_ind.description_en = self._read_config_value("INDICATOR", "snte_desc_en")
        snte_ind.description_es = self._read_config_value("INDICATOR", "snte_desc_es")
        snte_ind.description_fr = self._read_config_value("INDICATOR", "snte_desc_fr")
        share_measure.name = self._read_config_value("INDICATOR", "snte_unit_name")
        snte_ind.measurement_unit = share_measure
        snte_ind.topic = self._read_config_value("INDICATOR", "snte_topic")
        snte_ind.preferable_tendency = self._parse_preferable_tendency(
                                                    self._read_config_value("INDICATOR", "snte_tendency"))
        result[self.SNTE] = snte_ind

        # Shares in Number Operated as Others
        snot_ind = Indicator(chain_for_id=self._org_id,
                                     int_for_id=self._config.get("INDICATOR", "snot_id"))
        snot_ind.name_en = self._read_config_value("INDICATOR", "snot_name_en")
        snot_ind.name_es = self._read_config_value("INDICATOR", "snot_name_es")
        snot_ind.name_fr = self._read_config_value("INDICATOR", "snot_name_fr")
        snot_ind.description_en = self._read_config_value("INDICATOR", "snot_desc_en")
        snot_ind.description_es = self._read_config_value("INDICATOR", "snot_desc_es")
        snot_ind.description_fr = self._read_config_value("INDICATOR", "snot_desc_fr")
        share_measure.name = self._read_config_value("INDICATOR", "snot_unit_name")
        snot_ind.measurement_unit = share_measure
        snot_ind.topic = self._read_config_value("INDICATOR", "snot_topic")
        snot_ind.preferable_tendency = self._parse_preferable_tendency(
                                                    self._read_config_value("INDICATOR", "snot_tendency"))
        result[self.SNOT] = snot_ind
        
        # Shares in Area Operated as Owner
        saow_ind = Indicator(chain_for_id=self._org_id,
                                     int_for_id=self._config.get("INDICATOR", "saow_id"))
        saow_ind.name_en = self._read_config_value("INDICATOR", "saow_name_en")
        saow_ind.name_es = self._read_config_value("INDICATOR", "saow_name_es")
        saow_ind.name_fr = self._read_config_value("INDICATOR", "saow_name_fr")
        saow_ind.description_en = self._read_config_value("INDICATOR", "saow_desc_en")
        saow_ind.description_es = self._read_config_value("INDICATOR", "saow_desc_es")
        saow_ind.description_fr = self._read_config_value("INDICATOR", "saow_desc_fr")
        share_measure.name = self._read_config_value("INDICATOR", "saow_unit_name")
        saow_ind.measurement_unit = share_measure
        saow_ind.topic = self._read_config_value("INDICATOR", "saow_topic")
        saow_ind.preferable_tendency = self._parse_preferable_tendency(
                                                    self._read_config_value("INDICATOR", "saow_tendency"))
        result[self.SAOW] = saow_ind

        # Shares in Area Operated as Tenant
        sate_ind = Indicator(chain_for_id=self._org_id,
                                     int_for_id=self._config.get("INDICATOR", "sate_id"))
        sate_ind.name_en = self._read_config_value("INDICATOR", "sate_name_en")
        sate_ind.name_es = self._read_config_value("INDICATOR", "sate_name_es")
        sate_ind.name_fr = self._read_config_value("INDICATOR", "sate_name_fr")
        sate_ind.description_en = self._read_config_value("INDICATOR", "sate_desc_en")
        sate_ind.description_es = self._read_config_value("INDICATOR", "sate_desc_es")
        sate_ind.description_fr = self._read_config_value("INDICATOR", "sate_desc_fr")
        share_measure.name = self._read_config_value("INDICATOR", "sate_unit_name")
        sate_ind.measurement_unit = share_measure
        sate_ind.topic = self._read_config_value("INDICATOR", "sate_topic")
        sate_ind.preferable_tendency = self._parse_preferable_tendency(
                                                    self._read_config_value("INDICATOR", "sate_tendency"))
        result[self.SATE] = sate_ind

        # Shares in Area Operated as Others
        saot_ind = Indicator(chain_for_id=self._org_id,
                                     int_for_id=self._config.get("INDICATOR", "saot_id"))
        saot_ind.name_en = self._read_config_value("INDICATOR", "saot_name_en")
        saot_ind.name_es = self._read_config_value("INDICATOR", "saot_name_es")
        saot_ind.name_fr = self._read_config_value("INDICATOR", "saot_name_fr")
        saot_ind.description_en = self._read_config_value("INDICATOR", "saot_desc_en")
        saot_ind.description_es = self._read_config_value("INDICATOR", "saot_desc_es")
        saot_ind.description_fr = self._read_config_value("INDICATOR", "saot_desc_fr")
        share_measure.name = self._read_config_value("INDICATOR", "saot_unit_name")
        saot_ind.measurement_unit = share_measure
        saot_ind.topic = self._read_config_value("INDICATOR", "saot_topic")
        saot_ind.preferable_tendency = self._parse_preferable_tendency(
                                                    self._read_config_value("INDICATOR", "saot_tendency"))
        result[self.SAOT] = saot_ind

        # Number operated under more than one form of tenure
        nmo_ind = Indicator(chain_for_id=self._org_id,
                                     int_for_id=self._config.get("INDICATOR", "nmo_id"))
        nmo_ind.name_en = self._read_config_value("INDICATOR", "nmo_name_en")
        nmo_ind.name_es = self._read_config_value("INDICATOR", "nmo_name_es")
        nmo_ind.name_fr = self._read_config_value("INDICATOR", "nmo_name_fr")
        nmo_ind.description_en = self._read_config_value("INDICATOR", "nmo_desc_en")
        nmo_ind.description_es = self._read_config_value("INDICATOR", "nmo_desc_es")
        nmo_ind.description_fr = self._read_config_value("INDICATOR", "nmo_desc_fr")
        number_measure.name = self._read_config_value("INDICATOR", "nmo_unit_name")
        nmo_ind.measurement_unit = number_measure
        nmo_ind.topic = self._read_config_value("INDICATOR", "nmo_topic")
        nmo_ind.preferable_tendency = self._parse_preferable_tendency(
                                                    self._read_config_value("INDICATOR", "nmo_tendency"))
        result[self.NMO] = nmo_ind
        
        # Shares number operated under more than one form of tenure
        snmo_ind = Indicator(chain_for_id=self._org_id,
                                     int_for_id=self._config.get("INDICATOR", "snmo_id"))
        snmo_ind.name_en = self._read_config_value("INDICATOR", "snmo_name_en")
        snmo_ind.name_es = self._read_config_value("INDICATOR", "snmo_name_es")
        snmo_ind.name_fr = self._read_config_value("INDICATOR", "snmo_name_fr")
        snmo_ind.description_en = self._read_config_value("INDICATOR", "snmo_desc_en")
        snmo_ind.description_es = self._read_config_value("INDICATOR", "snmo_desc_es")
        snmo_ind.description_fr = self._read_config_value("INDICATOR", "snmo_desc_fr")
        share_measure.name = self._read_config_value("INDICATOR", "snmo_unit_name")
        snmo_ind.measurement_unit = share_measure
        snmo_ind.topic = self._read_config_value("INDICATOR", "snmo_topic")
        snmo_ind.preferable_tendency = self._parse_preferable_tendency(
                                                    self._read_config_value("INDICATOR", "snmo_tendency"))
        result[self.SNMO] = snmo_ind

        # Areas operated under more than one form of tenure
        amo_ind = Indicator(chain_for_id=self._org_id,
                                     int_for_id=self._config.get("INDICATOR", "amo_id"))
        amo_ind.name_en = self._read_config_value("INDICATOR", "amo_name_en")
        amo_ind.name_es = self._read_config_value("INDICATOR", "amo_name_es")
        amo_ind.name_fr = self._read_config_value("INDICATOR", "amo_name_fr")
        amo_ind.description_en = self._read_config_value("INDICATOR", "amo_desc_en")
        amo_ind.description_es = self._read_config_value("INDICATOR", "amo_desc_es")
        amo_ind.description_fr = self._read_config_value("INDICATOR", "amo_desc_fr")
        area_measure.name = self._read_config_value("INDICATOR", "amo_unit_name")
        amo_ind.measurement_unit = area_measure
        amo_ind.topic = self._read_config_value("INDICATOR", "amo_topic")
        amo_ind.preferable_tendency = self._parse_preferable_tendency(
                                                    self._read_config_value("INDICATOR", "amo_tendency"))
        result[self.AMO] = amo_ind
        
        # Shares number operated under more than one form of tenure
        samo_ind = Indicator(chain_for_id=self._org_id,
                                     int_for_id=self._config.get("INDICATOR", "samo_id"))
        samo_ind.name_en = self._read_config_value("INDICATOR", "samo_name_en")
        samo_ind.name_es = self._read_config_value("INDICATOR", "samo_name_es")
        samo_ind.name_fr = self._read_config_value("INDICATOR", "samo_name_fr")
        samo_ind.description_en = self._read_config_value("INDICATOR", "samo_desc_en")
        samo_ind.description_es = self._read_config_value("INDICATOR", "samo_desc_es")
        samo_ind.description_fr = self._read_config_value("INDICATOR", "samo_desc_fr")
        share_measure.name = self._read_config_value("INDICATOR", "samo_unit_name")
        samo_ind.measurement_unit = share_measure
        samo_ind.topic = self._read_config_value("INDICATOR", "samo_topic")
        samo_ind.preferable_tendency = self._parse_preferable_tendency(
                                                    self._read_config_value("INDICATOR", "samo_tendency"))
        result[self.SAMO] = samo_ind

        # Returning final dict
        return result

    def _read_config_value(self, section, field):
        return (self._config.get(section, field)).decode(encoding="utf-8")


    def _relate_common_objects(self):
        self._default_organization.add_user(self._default_user)
        self._default_organization.add_data_source(self._default_datasource)
        self._default_datasource.add_dataset(self._default_dataset)
        self._default_dataset.license_type = self._default_license
        # No return needed
