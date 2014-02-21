
from es.weso.countryrec.country_reconcilier import CountryReconcilier


def run():
    reconciler = CountryReconcilier()
    country = reconciler.get_country_by_un_code(533)
    print country.name


if __name__ == '__main__':
    run()
