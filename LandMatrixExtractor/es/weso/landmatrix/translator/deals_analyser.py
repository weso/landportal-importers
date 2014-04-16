from reconciler.country_reconciler import CountryReconciler
from reconciler.exceptions.unknown_country_error import UnknownCountryError


from .keys_dicts import KeyDicts
from ..entities.deal_analyser_entry import DealAnalyserEntry
from ..entities.deal import Deal

__author__ = 'Dani'


class DealsAnalyser(object):
    """
    It is built with a list of deal objects. When calling run, it return a dict that contains
    objetcs of type DealAnalyserEntry, containing a country, a date, an indicator and the composed
    value for the first two. Date will indicate the higher of the found dates

    """


    def __init__(self, deals_list, indicators_dict):
        self._list_deals = deals_list
        self._deals_dict = {}
        self._reconciler = CountryReconciler()
        self._observations_dict = {}
        self._indicators_dict = indicators_dict


    def run(self):
        for a_deal in self._list_deals:
            target_country = self._process_target_country(a_deal.target_country)
            if not target_country is None:
                self._process_the_fact_that_the_deal_has_valid_country(target_country)
                self._process_deals_by_negotiation_status(a_deal, target_country)
                self._process_deals_by_topic(a_deal, target_country)
                self._process_deals_by_hectares(a_deal, target_country)
                self._procces_date(a_deal, target_country)
            else:
                print "WOOOOOOO", a_deal.target_country

            # self._process_intended_hectares()

    def _process_target_country(self, target_country):
        try:
            return self._reconciler.get_country_by_en_name(target_country.encode(encoding="utf-8"))
        except UnknownCountryError:
            return None


    def _process_the_fact_that_the_deal_has_valid_country(self, target_country):
        self._increase_counter_indicator(KeyDicts.TOTAL_DEALS, target_country)


    def _process_deals_by_negotiation_status(self, deal, target_country):
        if deal.negotiation_status == Deal.CONCLUDED:
            self._increase_counter_indicator(KeyDicts.CONCLUDED_DEALS, target_country)
        elif deal.negotiation_status == Deal.FAILED:
            self._increase_counter_indicator(KeyDicts.FAILED_DEALS, target_country)
        elif deal.negotiation_status == Deal.INTENDED:
            self._increase_counter_indicator(KeyDicts.INTENDED_DEALS, target_country)


    def _procces_date(self, deal, target_country):
        compound_key = _get_compound_key(KeyDicts.TOTAL_DEALS, target_country)  # We have to get an entry of some
                                                                        #indicator, it does not matter which...
                                                                        #but we know that TOTAL_DEALS exists with                                                                     #no doucbt when reaching this point
        current_date = self._observations_dict[compound_key].date
        if deal.date is not None and deal.date > current_date:
            self._update_date_of_all_entrys_of_a_country(target_country, deal.date)

    def _update_date_of_all_entrys_of_a_country(self, country, date):
        self._update_date_of_an_entry(KeyDicts.TOTAL_DEALS, country, date)
        self._update_date_of_an_entry(KeyDicts.INTENDED_DEALS, country, date)
        self._update_date_of_an_entry(KeyDicts.CONCLUDED_DEALS, country, date)
        self._update_date_of_an_entry(KeyDicts.FAILED_DEALS, country, date)
        self._update_date_of_an_entry(KeyDicts.AGRICULTURE_DEALS, country, date)
        self._update_date_of_an_entry(KeyDicts.CONSERVATION_DEALS, country, date)
        self._update_date_of_an_entry(KeyDicts.FORESTRY_DEALS, country, date)
        self._update_date_of_an_entry(KeyDicts.INDUSTRY_DEALS, country, date)
        self._update_date_of_an_entry(KeyDicts.RENEWABLE_ENERGY_DEALS, country, date)
        self._update_date_of_an_entry(KeyDicts.TOURISM_DEALS, country, date)
        self._update_date_of_an_entry(KeyDicts.OTHER_DEALS, country, date)
        self._update_date_of_an_entry(KeyDicts.UNKNOWN_DEALS, country, date)
        self._update_date_of_an_entry(KeyDicts.HECTARES_TOTAL_DEALS, country, date)
        self._update_date_of_an_entry(KeyDicts.HECTARES_INTENDED_DEALS, country, date)
        self._update_date_of_an_entry(KeyDicts.HECTARES_CONTRACT_DEALS, country, date)
        self._update_date_of_an_entry(KeyDicts.HECTARES_PRODUCTION_DEALS, country, date)

    def _update_date_of_an_entry(self, deal_key, country, date):
        """
        It updates the date of the entry if it exists. If not, it simply returns without doing anything

        """
        compound_key = _get_compound_key(deal_key, country)
        if not compound_key in self._observations_dict:  # If there is no entry, nothing to do
            return
        else:
            self._observations_dict[compound_key].date = date


    def _process_deals_by_topic(self, deal, target_country):
        if Deal.AGRICULTURE in deal.sectors:
            self._increase_counter_indicator(KeyDicts.AGRICULTURE_DEALS, target_country)
        if Deal.CONSERVATION in deal.sectors:
            self._increase_counter_indicator(KeyDicts.CONSERVATION_DEALS, target_country)
        if Deal.FORESTRY in deal.sectors:
            self._increase_counter_indicator(KeyDicts.FORESTRY_DEALS, target_country)
        if Deal.INDUSTRY in deal.sectors:
            self._increase_counter_indicator(KeyDicts.INDUSTRY_DEALS, target_country)
        if Deal.RENEWABLE_ENERGY in deal.sectors:
            self._increase_counter_indicator(KeyDicts.RENEWABLE_ENERGY_DEALS, target_country)
        if Deal.TOURISM in deal.sectors:
            self._increase_counter_indicator(KeyDicts.TOURISM_DEALS, target_country)
        if Deal.OTHER in deal.sectors:
            self._increase_counter_indicator(KeyDicts.OTHER_DEALS, target_country)
        if Deal.UNKNOWN in deal.sectors:
            self._increase_counter_indicator(KeyDicts.UNKNOWN_DEALS, target_country)


    def _process_deals_by_hectares(self, deal, target_country):
        max_hectares = None
        if not deal.production_hectares is None:
            max_hectares = self._update_max_hectares(max_hectares, deal.production_hectares)
            self._increase_hectares_indicator(KeyDicts.HECTARES_PRODUCTION_DEALS,
                                              deal.production_hectares,
                                              target_country)
        if not deal.intended_hectares is None:
            max_hectares = self._update_max_hectares(max_hectares, deal.intended_hectares)
            self._increase_hectares_indicator(KeyDicts.HECTARES_INTENDED_DEALS,
                                              deal.intended_hectares,
                                              target_country)
        if not deal.contract_hectares is None:
            max_hectares = self._update_max_hectares(max_hectares, deal.contract_hectares)
            self._increase_hectares_indicator(KeyDicts.HECTARES_CONTRACT_DEALS,
                                              deal.contract_hectares,
                                              target_country)
        if not max_hectares is None:
            self._increase_hectares_indicator(KeyDicts.HECTARES_TOTAL_DEALS,
                                              max_hectares,
                                              target_country)
        pass


    @staticmethod
    def _update_max_hectares(old_hectares, new_hectares):
        """
        It simply return the max value of the received ones. The problem is that old_hectares could be None.
        We expect new_hectares to not be None

        """
        if old_hectares is None:
            return new_hectares
        elif old_hectares > new_hectares:
            return old_hectares
        else:
            return new_hectares



    def _increase_hectares_indicator(self, deal_key, hectares, country):
        """
        It increases in "max_hectares" the value of the entry under the key "deal_key + country"
        If the entry does not exist in the internal dict, it creates it.
        """
        compound_key = _get_compound_key(deal_key, country)

        #Creating new entry if needed
        if not compound_key in self._observations_dict:
            new_entry = DealAnalyserEntry(indicator=self._indicators_dict[deal_key],
                                          country=country,
                                          date=None,
                                          value=0)
            self._observations_dict[compound_key] = new_entry

        #Updating entry
        entry = self._observations_dict[compound_key]
        entry.value += hectares
        #Done, no return needed




    def _increase_counter_indicator(self, deal_key, country):
        """
        Increase in one unit the value of the appropiate entry in observations_dict
        If the entry does not exist, it also creates it

        """
        compound_key = _get_compound_key(deal_key, country)

        #Creating new entry in obs_dict if needed
        if not compound_key in self._observations_dict:
            new_entry = DealAnalyserEntry(indicator=self._indicators_dict[deal_key],
                                          country=country,
                                          date=None,
                                          value=0)
            self._observations_dict[compound_key] = new_entry
        #Updating entry
        entry = self._observations_dict[compound_key]
        entry.value += 1
        #Done. No return needed



##################################################################
#                            FUNCTIONS                           #
##################################################################


def _get_compound_key(deal_key, country):
    return str(deal_key) + country.iso3