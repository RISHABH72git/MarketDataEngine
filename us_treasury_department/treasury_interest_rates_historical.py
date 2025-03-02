from enum import Enum
from io import StringIO

import pandas as pd
import requests

INTEREST_RATES_URL = "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/"


class InterestRatesType(Enum):
    """ Enum for different types of Interest Rates Types"""
    Daily_Treasury_Par_Yield_Curve_Rates = ("daily_treasury_yield_curve", 1990)
    Daily_Treasury_Bill_Rates = ("daily_treasury_bill_rates", 2002)
    Daily_Treasury_Long_Term_Rates = ("daily_treasury_long_term_rate", 2000)
    Daily_Treasury_Par_Real_Yield_Curve_Rates = ("daily_treasury_real_yield_curve", 2003)
    Daily_Treasury_Real_Long_Term_Rates = ("daily_treasury_real_long_term", 2000)


class TreasuryInterestRatesHistorical:
    @staticmethod
    def fetch_and_store(interest_rates_type: InterestRatesType, start_year: int, end_year: int):
        """Fetch and store interest rates data for a given type.
        :param interest_rates_type: Type of interest rates (Enum)
        :param start_year: Year from which to start downloading
        :param end_year: Year to which to stop downloading
        """
        rates_type = interest_rates_type.value[0]
        base_year = interest_rates_type.value[1]
        print(f"Fetching {interest_rates_type.name} data for {base_year} year")
        url_list = {}
        if start_year and end_year:
            if start_year < base_year:
                start_year = base_year

            while start_year <= end_year:
                url_list[
                    start_year] = f"{INTEREST_RATES_URL}{start_year}/all?type={rates_type}&field_tdr_date_value={start_year}&page&_format=csv"
                start_year += 1

        if url_list:
            with requests.Session() as session:
                for key, url in url_list.items():
                    print(f"Downloading: {url}")
                    try:
                        response = session.get(url, timeout=30)
                        if response.status_code == 200:
                            csv_data = StringIO(response.text)
                            pd.read_csv(csv_data).to_csv(f"{key}_{rates_type}.csv", index=False)
                        else:
                            print(f"Failed to fetch data for {key}. HTTP Status:", response.status_code)
                    except requests.exceptions.RequestException as e:
                        print(f"Failed to fetch {url}: {e}")


if __name__ == '__main__':
    fetcher = TreasuryInterestRatesHistorical()
    fetcher.fetch_and_store(InterestRatesType.Daily_Treasury_Par_Yield_Curve_Rates, 2024, 2025)
    fetcher.fetch_and_store(InterestRatesType.Daily_Treasury_Bill_Rates, 2024, 2025)
    fetcher.fetch_and_store(InterestRatesType.Daily_Treasury_Long_Term_Rates, 2024, 2025)
    fetcher.fetch_and_store(InterestRatesType.Daily_Treasury_Par_Real_Yield_Curve_Rates, 2024, 2025)
    fetcher.fetch_and_store(InterestRatesType.Daily_Treasury_Real_Long_Term_Rates, 2024, 2025)
