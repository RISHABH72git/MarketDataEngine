import zipfile
from datetime import date
from enum import Enum
from io import BytesIO

import pandas as pd
import requests

BASE_URL = "https://www.cftc.gov/files/dea/history/"
BASE_PATH = None


class COTReportType(Enum):
    """ Enum for different types of COT reports """
    Disaggregated_Futures_Only_Reports = ("fut_disagg_xls", (2006, 2016))
    Disaggregated_Futures_and_Options_Combined_Reports = ("com_disagg_xls", (2006, 2016))
    Traders_in_Financial_Futures_Only_Reports = ("fut_fin_xls", (2006, 2016))
    Traders_in_Financial_Futures_and_Options_Combined_Reports = ("com_fin_xls", (2006, 2016))
    Commodity_Index_Trader_Supplement = ("dea_cit_xls", (2006, 2016))


class COTDataFetcher:
    """ Class to fetch and store Commitment of Traders (COT) data """

    @staticmethod
    def fetch_and_store(report_type: COTReportType, start_year: int):
        """Fetch and store COT data for a given report type.
        :param report_type: Type of COT report (Enum)
        :param start_year: Year from which to start downloading
        """
        file_prefix = report_type.value[0]
        historical_range = report_type.value[1]
        # Download historical data (if applicable)
        url_list = {}
        if historical_range and start_year <= historical_range[1]:
            start, end = historical_range
            historical_file = f"{BASE_URL}{file_prefix}_hist_{start}_{end}.zip"
            url_list[f"{start}_{end}"] = historical_file
            start_year = end + 1

        # Download data for each year
        while start_year <= date.today().year:
            yearly_file = f"{BASE_URL}{file_prefix}_{start_year}.zip"
            url_list[start_year] = yearly_file
            start_year += 1

        with requests.Session() as session:
            for key, url in url_list.items():
                print(f"Downloading: {url}")
                try:
                    response = session.get(url, timeout=10)
                    response.raise_for_status()
                    COTDataFetcher._process_zip(response.content, key)
                except requests.exceptions.RequestException as e:
                    print(f"Failed to fetch {url}: {e}")

    @staticmethod
    def _process_zip(zip_content, key):
        """Extract Excel files from ZIP and convert to CSV."""
        zip_data = BytesIO(zip_content)
        with zipfile.ZipFile(zip_data, 'r') as z:
            file_list = z.namelist()
            for file_name in file_list:
                if file_name.endswith('.xls') or file_name.endswith('.xlsx'):
                    with z.open(file_name) as file:
                        df = pd.read_excel(file)
                        saved_file_path = f"{key}_{file_name}"
                        if BASE_PATH:
                            saved_file_path = f"{BASE_PATH}{saved_file_path}"

                        df.to_csv(saved_file_path, index=False)


if __name__ == "__main__":
    fetcher = COTDataFetcher()
    fetcher.fetch_and_store(COTReportType.Disaggregated_Futures_Only_Reports, 2006)
    fetcher.fetch_and_store(COTReportType.Disaggregated_Futures_and_Options_Combined_Reports, 2006)
    fetcher.fetch_and_store(COTReportType.Traders_in_Financial_Futures_Only_Reports, 2006)
    fetcher.fetch_and_store(COTReportType.Traders_in_Financial_Futures_and_Options_Combined_Reports, 2006)
    fetcher.fetch_and_store(COTReportType.Commodity_Index_Trader_Supplement, 2006)
