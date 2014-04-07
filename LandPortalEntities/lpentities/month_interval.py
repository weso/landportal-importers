__author__ = 'Dani'


from .interval import Interval


class MonthInterval(Interval):

    def __init__(self, year, month):
        self.year = year
        self.month = month
        arg_for_super = self.get_time_string()  # We do not have to call the method two times
        super(MonthInterval, self).__init__(arg_for_super, arg_for_super)

    def get_time_string(self):
        str_month = str(self.month)
        if len(str_month) == 1:
            str_month = "0" + str_month

        return str_month + "/" + str(self.year)