from datetime import datetime

from lpentities.computation import Computation
from lpentities.data_source import DataSource
from lpentities.dataset import Dataset
from lpentities.indicator import Indicator
from lpentities.instant import Instant
from lpentities.interval import Interval
from lpentities.license import License
from lpentities.measurement_unit import MeasurementUnit
from lpentities.month_interval import MonthInterval
from lpentities.observation import Observation
from lpentities.organization import Organization
from lpentities.user import User
from lpentities.value import Value
from lpentities.year_interval import YearInterval
from model2xml.model2xml import ModelToXMLTransformer
from reconciler.country_reconciler import CountryReconciler

from weso.raw.ExcelManagement.excel_reader import XslReader


__author__ = 'BorjaGB'

class RawImporter(object):

    def __init__(self, log, config, org_id, file_name, look_for_historical):
        self._log = log
        self._config = config
        self._file_name = file_name
        self._look_for_historical = look_for_historical
        if not look_for_historical:
            self._historical_year = self._config.getint("TRANSLATOR", "historical_year")
        self._reconciler = CountryReconciler()

        # Initializing variable ids
        self._org_id = org_id
        self._ind_int = self._config.getint("TRANSLATOR", "ind_int")
        self._obs_int = self._config.getint("TRANSLATOR", "obs_int")
        self._sli_int = self._config.getint("TRANSLATOR", "sli_int")
        self._dat_int = self._config.getint("TRANSLATOR", "dat_int")
        self._igr_int = self._config.getint("TRANSLATOR", "igr_int")

        # Building parsing instances
        self._xsl_reader = self._build_xsl_reader()
        
        # Excel data
        self._indicator_sheet_dictionary = self._load_indicator_data()
        self._organization_sheet_dictionary = self._load_organization_data()
        
        try:
            self.custom_ind_int = self._config.getint(self._indicator_sheet_dictionary["English name"], "id")
            self.custom_dat_int = self._config.getint(self._indicator_sheet_dictionary["English name"], "dataset")
        except:
            pass
        
        self._indicator = self._build_indicator()
        
        self._organization = self._build_organization()
        self._license = self._build_license()
        
        print self._indicator.description_es
        
        # Building common objects
        self._default_user = self._build_default_user()
        self._datasource = self._build_default_datasource()
        self._dataset = self._build_default_dataset()
        self._relate_common_objects()
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
        observations = self._load_observations_data()
        if len(observations) > 0:
            for obs in observations :
                self._dataset.add_observation(obs)
        else:
            print "No observations found"
        # Send model for its trasnlation
        translator = ModelToXMLTransformer(self._dataset, "API_REST", self._default_user)
        translator.run()

        # And it is done. No return needed

    def _build_xsl_reader(self):
        return XslReader()
    
    def _load_indicator_data(self):
        return self._xsl_reader.load_indicator_sheet(self._file_name)

    def _build_indicator(self):
        if hasattr(self, 'custom_ind_int'):
            ind_int = self.custom_ind_int
        else:
            self._ind_int+=1
            ind_int = self._ind_int
            
        return Indicator(chain_for_id=self._org_id,
                         int_for_id=ind_int,
                         name_en=self._indicator_sheet_dictionary["English name"],
                         name_es=self._indicator_sheet_dictionary["Spanish name"],
                         name_fr=self._indicator_sheet_dictionary["French name"], 
                         description_en=self._indicator_sheet_dictionary["English description"],
                         description_es=self._indicator_sheet_dictionary["Spanish description"],
                         description_fr=self._indicator_sheet_dictionary["French description"],
                         measurement_unit= MeasurementUnit(name= self._indicator_sheet_dictionary["Measurement unit"],
                                                           convert_to = self._indicator_sheet_dictionary["Convertible to"],
                                                           factor = self._indicator_sheet_dictionary["Conversion factor"]),
                         preferable_tendency=self._get_preferable_tendency_of_indicator(self._indicator_sheet_dictionary["Preferable tendency"]),
                         topic=self._get_topic_of_indicator(self._indicator_sheet_dictionary["Topic"]))
    
    def _load_organization_data(self):
        return self._xsl_reader.load_organization_sheet(self._file_name)

    def _build_organization(self):
        return Organization(chain_for_id=self._org_id,
                            name = self._organization_sheet_dictionary["Name"],
                            url = self._organization_sheet_dictionary["URL"],
                            url_logo = self._organization_sheet_dictionary["Logo"],
                            description_en = self._organization_sheet_dictionary["Description_EN"],
                            description_es = self._organization_sheet_dictionary["Description_ES"],
                            description_fr = self._organization_sheet_dictionary["Description_FR"] )

    def _build_license(self):
        result = License()
        if self._organization_sheet_dictionary["License_Republish"] == "Yes":
            result.republish = True
        else:
            result.republish = False
        result.description = self._organization_sheet_dictionary["License_Description"]
        result.name = self._organization_sheet_dictionary["License_Name"]
        result.url = self._organization_sheet_dictionary["License_URL"]

        return result
    
    def _load_observations_data(self):
        result = []
        data = self._xsl_reader.load_xsl(self._file_name)
        for i in range(1, len(data)):
            country = self._get_country_by_name(data[i][0])
            if country is not None :
                for j in range(1, len(data[0])):
                    year = self._build_ref_time_object(data[0][j])
                    if self._filter_historical_observations(year):
                        value = self._build_value_object(data[i][j])
                        result.append(self._build_observation_for_cell(year,
                                                                       value,
                                                                       country))
        
        return result
    
    def _filter_historical_observations(self, year): 
        if self._look_for_historical:
            return True
        else :
            if isinstance(year, YearInterval):
                return year.year > self._historical_year
            else:
                return year.end_time > self._historical_year 
    
    def _build_observation_for_cell(self, year, value, country):
        result = Observation(chain_for_id=self._org_id, int_for_id=self._obs_int)
        self._obs_int += 1  # Updating id value
        
        result.indicator = self._indicator
        result.value = value
        result.computation = self._get_computation_object()  # Always the same, no param needed
        result.issued = self._build_issued_object()  # No param needed
        result.ref_time = year
        country.add_observation(result)  # And that stablish the relation in both directions
        
        return result
    
    def _build_ref_time_object(self, time):
        if self._dataset.frequency == Dataset.MONTHLY:
            months = str(time).split("-")
            if len(months) == 1:
                month_time = months[0].split("/") #01/1990
                return MonthInterval(year = month_time[1], month = month_time[0])
            else:
                return Interval(frequency = Interval.MONTHLY, start_time=months[0], end_time=months[1])
        else:
            years = str(time).split("-")
            if len(years) == 1:
                return YearInterval(year=int(time))
            else :
                return Interval(start_time=int(years[0]), end_time=int(years[1]))
            
    def _build_issued_object(self):
        return Instant(datetime.now())

    def _get_computation_object(self):
        return self._default_computation

    @staticmethod
    def _build_value_object(value):
        result = Value(value=None,
                       value_type=Value.MISSING,
                       obs_status=Value.MISSING)
        
        if not (value is None or value == "-"):
            try:
                result.value = int(value)
                result.value_type = Value.INTEGER
                result.obs_status = Value.AVAILABLE
                return result
            except: #Is not integer value 
                try: #Try with float
                    result.value = float(value)
                    result.value_type = Value.FLOAT
                    result.obs_status = Value.AVAILABLE
                except:
                    return result
        else:
            return result
        
    def _get_country_by_name(self, country_name):
        country = None
        try: 
            country = self._reconciler.get_country_by_en_name(country_name)
        except:
            country = None
        
        return country

    def _build_default_user(self):
        return User(user_login="RAWIMPORTER")

    def _build_default_datasource(self):
        result = DataSource(chain_for_id=self._org_id,
                            int_for_id=1)
        result.name = self._indicator_sheet_dictionary["Data source"]
        
        return result

    def _build_default_dataset(self):
        if hasattr(self, 'custom_dat_int'):
            dat_int = self.custom_dat_int
        else:
            self._dat_int += 1  # Needed increment
            dat_int = self._dat_int
            
        result = Dataset(chain_for_id=self._org_id, int_for_id=dat_int)
        if self._indicator_sheet_dictionary["Periodicity"].lower() == "yearly":
            result.frequency = Dataset.YEARLY
        else:
            result.frequency = Dataset.MONTHLY
        return result

    @staticmethod
    def _get_preferable_tendency_of_indicator(tendency):
        if tendency.lower() == "the lower the best":
            return Indicator.DECREASE
        elif tendency.lower() == "the higher the best":
            return Indicator.INCREASE
        else:
            return Indicator.IRRELEVANT
    
    @staticmethod
    def _get_topic_of_indicator(topic):
        lower_topic = topic.lower()
        
        if lower_topic == "geographic and socio economic":
            return "GEOGRAPH_SOCIO"
        elif lower_topic == "land use agriculture and investment":
            return "LAND_USE"
        elif lower_topic == "climate change":
            return "CLIMATE_CHANGE"
        elif lower_topic == "food security and hunger":
            return "FSECURITY_HUNGER"
        elif lower_topic == "land and gender":
            return "LAND_GENDER"
        elif lower_topic == "land use":
            return "LAND_USE"
        else:
            return "TOPIC_TEMP"
        
    def _relate_common_objects(self):
        self._organization.add_user(self._default_user)
        self._organization.add_data_source(self._datasource)
        self._datasource.add_dataset(self._dataset)
        self._dataset.license_type = self._license
        # No return needed
