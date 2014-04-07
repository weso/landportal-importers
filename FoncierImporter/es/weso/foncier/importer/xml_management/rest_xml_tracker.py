__author__ = 'Dani'

import requests


class RestXmlTracker(object):

    def __init__(self, url_pattern, year_pattern, month_pattern):
        self._url_pattern = url_pattern
        self._year_pattern = year_pattern
        self._month_pattern = month_pattern

    def track_xml(self, year, month):
        url = self._prepare_url(year, month)
        return requests.get(url).content

    def _prepare_url(self, year, month):
        result = self._url_pattern.replace(self._year_pattern, str(year))
        result = result.replace(self._month_pattern, str(month))
        return result


