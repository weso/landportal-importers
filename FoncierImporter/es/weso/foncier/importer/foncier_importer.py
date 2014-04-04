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

from reconciler.country_reconciler import CountryReconciler
from model2xml.model2xml import ModelToXMLTransformer

from ..exceptions.no_new_data_available_error import NoNewDataAvailableError



class FoncierImporter(object):


    def __init__(self, log, config, look_for_historical):
        self._log = log
        self._config = config
        self._look_for_historical = look_for_historical
        self._reconciler = CountryReconciler()

        # Building common objects
        self._default_user = self._build_default_user()  # TODO
        self._default_datasource = self._build_default_datasource()  # TODO
        self._default_dataset = self._build_default_dataset()  # TODO
        self._default_organization = self._build_default_organization()  # TODO
        self._default_license = self._build_default_license()  # TODO
        self._relate_common_objects()  # TODO
        self._default_country = self._get_default_country()  # Done =)

        # Objects that will be needed during the parsing process
        #Initializing variable ids
        self._indicators_dict = self._build_indicators_dict()
        self._org_id = self._config.get("TRANSLATOR", "org_id")
        self._obs_int = int(self._config.get("TRANSLATOR", "obs_int"))
        self._sli_int = int(self._config.get("TRANSLATOR", "sli_int"))
        self._dat_int = int(self._config.get("TRANSLATOR", "dat_int"))
        self._igr_int = int(self._config.get("TRANSLATOR", "igr_int"))
        self._ind_int = int(self._config.get("TRANSLATOR", "ind_int"))
        self._sou_int = int(self._config.get("TRANSLATOR", "sou_int"))


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
            #TODO: make something noisy
            return  # It is quite noisy eh?

        #Generate observations and incorpore it to the common objects
        observations = self._build_observations_from_available_years(first_year, last_year)
        for obs in observations:
            self._default_dataset.add_observation(obs)

        #Send model for its trasnlation
        translator = ModelToXMLTransformer(self._default_dataset, "API_REST", self._default_user)
        translator.run()

        #Actualizing config values in case of success
        self._actualize_config_values(last_year)

        #And it is done. No return needed

    def _actualize_config_values(self, last_year):
        #TODO: ids int values and last checked year
        pass

    def _build_observations_from_available_years(self, first_year, last_year):
        result = []
        for year in range(first_year, last_year + 1):
            result += self._build_observations_from_a_single_year(year)
        return result

    def _build_observations_from_a_single_year(self, year):
        result =[]
        for month in range(1,13):
            result.append(self._build_observation_from_a_concrete_month(year, month))
        return result

    def _build_observation_from_a_concrete_month(self, year, month):
        # TODO: Do everythin! Call the API, parse the result,...
        pass

    def _determine_years_to_query(self):
        first_year = int(self._config.get("AVAILABLE_TIME", "first_year"))
        last_year = int(self._config.get("AVAILABLE_TIME", "last_year"))

        if not self._look_for_historical:
            return first_year, last_year
        else:
            last_checked = int(self._config.get("AVAILABLE_TIME", "last_checked_year"))
            if last_year <= last_checked:
                raise NoNewDataAvailableError("No new data available. Source has not been updated since last execution")
            else:
                return last_checked + 1, last_year


    def _get_default_country(self):
        return self._reconciler.get_country_by_iso3("MDG")
        pass

    def _build_default_user(self):
        return "a"

    def _build_default_datasource(self):
        return "a"

    def _build_default_dataset(self):
        result = Dataset(chain_for_id=self._org_id, int_for_id=self._dat_int)
        self._dat_int += 1  # Needed increment
        return result

    def _build_default_organization(self):
        return "a"

    def _build_default_license(self):
        return "a"

    def _build_indicators_dict(self):
        return "a"

    def _relate_common_objects(self):
        #No return needed
        pass
