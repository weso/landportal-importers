__author__ = 'Dani'


from .interval import Interval


class MonthInterval(Interval):

    def __init__(self, year, month):
        self._year = year
        self._month = month
        arg_for_super = self.get_time_string()  # We do not have to call the method two times
        super(MonthInterval, self).__init__(Interval.MONTHLY, arg_for_super, arg_for_super)

    def __get_year(self):
        return self._year
    
    def __set_year(self, year):
        try:
            if len(str(year)) == 4 :
                self._year = int(year)
            else:
                raise ValueError("Year must have yyyy format")
        except:
            raise ValueError("Year must be an integer")
        
    year = property(fget=__get_year,
                      fset=__set_year,
                      doc="The year of the given month")

    def __get_month(self):
        return self._month
    
    def __set_month(self, month):
        try:
            self._month = int(month)
        except:
            raise ValueError("Month must be an integer")
        
    month = property(fget=__get_month,
                      fset=__set_month,
                      doc="The month of the observation")

    def get_time_string(self):
        str_month = str(self.month)
        if len(str_month) == 1:
            str_month = "0" + str_month

        return str_month + "/" + str(self.year)