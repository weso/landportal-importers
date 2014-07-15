__author__ = 'Dani'

import requests
from requests.adapters import HTTPAdapter


class RestXmlTracker(object):

    def __init__(self, url_pattern_month, url_pattern_year, year_pattern, month_pattern):
        self._url_pattern = url_pattern_month
        self._url_pattern_year = url_pattern_year
        self._year_pattern = year_pattern
        self._month_pattern = month_pattern

    def track_xml(self, year, month):
        """
        Sometimes the server block us or fail. We sould retry
        """
        url = self._prepare_url(year, month)
        s = requests.Session()
        s.mount(url, HTTPAdapter(max_retries=10))
        result = requests.get(url).content
        return result

    def _prepare_url(self, year, month):
        if month is not None:
            result = self._url_pattern.replace(self._year_pattern, str(year))
            return result.replace(self._month_pattern, str(month))
        else:
            return self._url_pattern_year.replace(self._year_pattern, str(year))


