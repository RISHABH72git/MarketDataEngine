import requests


class NasdaqAPI:
    BASE_URL = "https://api.nasdaq.com/api"

    def __init__(self, user_agent=None):
        self.headers = {
            "connection": "keep-alive",
            "authority": "api.nasdaq.com",
            "method": "GET",
            "scheme": "https",
            "accept": "application/json, text/plain, */*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-GB,en;q=0.6",
            "origin": "https://www.nasdaq.com",
            "referer": "https://www.nasdaq.com/",
            "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Brave";v="134"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Linux"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "sec-gpc": "1",
            "user-agent": user_agent or "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
                                        "Chrome/134.0.0.0 Safari/537.36",
        }

    def fetch_data(self, endpoint, params=None):
        """Fetches data from any Nasdaq API endpoint."""
        url = f"{self.BASE_URL}/{endpoint}"
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()  # Raise an error for 4xx and 5xx responses
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {endpoint}: {e}")
            return None

    def market_info(self):
        """Fetch earnings calendar for a given date."""
        return self.fetch_data("market-info")

    def get_earnings_calendar(self, date):
        """Fetch earnings calendar for a given date."""
        return self.fetch_data("calendar/earnings", {"date": date})

    def get_dividends_calendar(self, date):
        """Fetch dividends calendar for a given date."""
        return self.fetch_data("calendar/dividends", {"date": date})

    def get_ipos_calendar(self, date):
        """Fetch IPO calendar for a given date."""
        return self.fetch_data("ipo/calendar", {"date": date})

    def get_economic_calendar(self, date):
        """Fetch economic calendar for a given date."""
        return self.fetch_data("calendar/economicevents", {"date": date})

    def search_stocks(self, search):
        """Fetch list of symbols for a given search string."""
        return self.fetch_data("autocomplete/slookup/10", {"search": search})

    def indices_total_returns(self):
        """Fetch details of total returns for a indices."""
        return self.fetch_data("/quote/list-type/totalreturns")


if __name__ == "__main__":
    nasdaq_api = NasdaqAPI()
    total_returns = nasdaq_api.indices_total_returns()
    print(total_returns)
    # market_info = nasdaq_api.market_info()
    # print("market info ", market_info)
    #
    # # Fetch Earnings Data
    # earnings_data = nasdaq_api.get_earnings_calendar("2025-03-04")
    # print("Earnings Data:", earnings_data)

    # Fetch Dividends Data
    # dividends_data = nasdaq_api.get_dividends_calendar("2025-03-04")
    # print("Dividends Data:", dividends_data)
    #
    # # Fetch IPO Data
    # ipos_data = nasdaq_api.get_ipos_calendar("2025-03")
    # print("IPO Data:", ipos_data)
    #
    # economic_calendar = nasdaq_api.get_economic_calendar("2025-03-04")
    # print("economic_calendar:", economic_calendar)
