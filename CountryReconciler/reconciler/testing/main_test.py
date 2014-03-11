# -*- coding: utf-8 -*-

__author__ = 'Miguel Otero'

import unittest

from reconciler.country_reconciler import CountryReconciler
from reconciler.exceptions.unknown_country_error import UnknownCountryError


class ReconcilerTest(unittest.TestCase):

    COUNTRIES_IN_FILE = 248

    def setUp(self):
        self.reconciler = CountryReconciler()

    def test_parse_countries(self):
        self.assertEqual(len(self.reconciler.parsed_countries),
                         self.COUNTRIES_IN_FILE,
                         "Unexpected number of countries. Encountered "
                         + str(len(self.reconciler.parsed_countries))
                         + ', expected ' + str(self.COUNTRIES_IN_FILE))

    def test_get_country_by_iso2(self):
        spain = self.reconciler.get_country_by_iso2('ES')
        self.assertEqual(spain.iso3, 'ESP')
        self.assertEqual(spain.name, 'Spain')
        with self.assertRaises(UnknownCountryError):
            self.reconciler.get_country_by_iso2('XX')

    def test_get_country_by_un_code(self):
        austria = self.reconciler.get_country_by_un_code(40)
        self.assertEqual(austria.iso3, 'AUT')
        self.assertEqual(austria.name, 'Austria')
        with self.assertRaises(UnknownCountryError):
            self.reconciler.get_country_by_un_code(-666)

    def test_get_country_by_faostat_code(self):
        aruba = self.reconciler.get_country_by_faostat_code(22)
        self.assertEqual(aruba.iso3, 'ABW')
        self.assertEqual(aruba.name, 'Aruba')
        with self.assertRaises(UnknownCountryError):
            self.reconciler.get_country_by_faostat_code(-666)

    def test_get_country_by_en_name(self):
        spain = self.reconciler.get_country_by_en_name('Spain')
        self.assertEqual(spain.iso3, 'ESP', 'Unexpected ISO3. Encountered ' + str(spain.iso3) + ', expected ESP')
        self.assertEqual(spain.name, 'Spain')
        weird_spain = self.reconciler.get_country_by_en_name('SpáÏn')
        self.assertEqual(weird_spain.iso3, 'ESP', 'Unexpected ISO3. Encountered ' + str(weird_spain.iso3) + ', expected ESP')
        self.assertEqual(weird_spain.name, 'Spain')
        long_spain = self.reconciler.get_country_by_en_name('Spain (parliamentary monarchy)')
        self.assertEqual(long_spain.iso3, 'ESP', 'Unexpected ISO3. Encountered ' + str(long_spain.iso3) + ', expected ESP')
        self.assertEqual(long_spain.name, 'Spain')
        curacao = self.reconciler.get_country_by_en_name('Curaþao')
        self.assertEqual(curacao.iso3, 'CUW', 'Unexpected ISO3. Encountered ' + str(curacao.iso3) + ', expected CUW')
        self.assertEqual(curacao.name, 'Curaþao')
        with self.assertRaises(UnknownCountryError):
            self.reconciler.get_country_by_en_name('Spai')

    def test_conflictive_ipfri(self):
        #We expect to non have any exception with the next calls
        central_african_rep = self.reconciler.get_country_by_en_name("Central African Rep.")
        central_african_rep = self.reconciler.get_country_by_en_name("Congo, Dem. Rep.")
        central_african_rep = self.reconciler.get_country_by_en_name("Congo, Rep.")
        central_african_rep = self.reconciler.get_country_by_en_name("Egypt, Arab Rep.")
        central_african_rep = self.reconciler.get_country_by_en_name("Iran, Islamic Rep.")
        central_african_rep = self.reconciler.get_country_by_en_name("Kyrgyz Republic")
        central_african_rep = self.reconciler.get_country_by_en_name("Lao PDR")
        central_african_rep = self.reconciler.get_country_by_en_name("Macedonia, FYR")
        central_african_rep = self.reconciler.get_country_by_en_name("North Korea")
        central_african_rep = self.reconciler.get_country_by_en_name("Russian Federation")
        central_african_rep = self.reconciler.get_country_by_en_name("Slovak Republic")
        central_african_rep = self.reconciler.get_country_by_en_name("Tanzania")
        central_african_rep = self.reconciler.get_country_by_en_name("Venezuela, RB")
        central_african_rep = self.reconciler.get_country_by_en_name("Yemen, Rep.")


if __name__ == '__main__':
    unittest.main()
