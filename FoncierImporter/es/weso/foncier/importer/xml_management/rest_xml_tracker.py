__author__ = 'Dani'

import requests
from requests.adapters import HTTPAdapter


class RestXmlTracker(object):

    def __init__(self, url_pattern, year_pattern, month_pattern):
        self._url_pattern = url_pattern
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
        result = self._url_pattern.replace(self._year_pattern, str(year))
        result = result.replace(self._month_pattern, str(month))
        return result


