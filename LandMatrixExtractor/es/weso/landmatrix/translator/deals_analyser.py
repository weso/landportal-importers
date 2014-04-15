from reconciler.country_reconciler import CountryReconciler
from reconciler.exceptions.unknown_country_error import UnknownCountryError

from lpentities.indicator import Indicator
from lpentities.measurement_unit import MeasurementUnit

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
                self._process_production_hectares(a_deal, target_country)
                self._process_contract_hectares(a_deal, target_country)
                self._process_intended_hectares(a_deal, target_country)
                self._process_date(a_deal, target_country)
                #TODO: Continue here!
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


    def _process_deals_by_topic(self, deal, target_country):
        #TODO: cONTINUE HERE
        pass

    def _process_production_hectares(self, deal, target_country):
        #TODO: we haven't done anything yet
        pass

    def _increase_counter_indicator(self, deal_key, country):
        """
        Increase in one unit the value of the appropiate entry in observations_dict
        If teh entry does not exist, it also creates it

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








def _get_compound_key(deal_key, country):
    return str(deal_key) + country.iso3