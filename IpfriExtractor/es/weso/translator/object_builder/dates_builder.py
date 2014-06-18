__author__ = 'Dani'

from lpentities.year_interval import YearInterval
from lpentities.interval import Interval


def get_model_object_time_from_parsed_string(original_time):
    str_time = str(original_time).replace(" ", "")  # we could already receive a str, but we need to ensure it
    if "-" in str_time:
        return _get_model_object_interval(str_time)
    else:
        return _get_model_object_year_interval(str_time)


def _get_model_object_interval(str_time):
    date_array = str_time.split("-")
    start_time = int(date_array[0])
    end_time = _transform_twodigited_date_into_forudigited_if_needed(date_array[1])
    return Interval(start_time=start_time, end_time=end_time)


def _get_model_object_year_interval(str_time):
    return YearInterval(year=int(float(str_time)))


def _transform_twodigited_date_into_forudigited_if_needed(indef_digited_str):
    """
    We are turning the string into an int. Depending on its value, we add a quantity to that int, obtaining the year.
    Examples:
        receiving 10:
        10 + 2000 = 2010. return 2010 as year
        receiving 98:
        98 + 1900 = 1998. return 1998 as a year

    """
    if len(indef_digited_str) == 4:
        return int(indef_digited_str)
    d2f = int(indef_digited_str)
    if d2f < 50:
        d2f += 2000
    elif d2f >= 50:
        d2f += 1900
    return d2f

    #  The function will stop working in 2050...