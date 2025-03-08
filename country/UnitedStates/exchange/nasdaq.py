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

    def get_52_week_high_low(self, exchange="q", status="Low", limit=99999, sort_column="symbol", sort_order="ASC"):
        """
        Fetches 52-week high/low data from Nasdaq.

        :param exchange: Stock exchange (default is "q" for NASDAQ, 14 for NYSE, 1 for AMEX).
        :param status: "Hi" or "Low" (default is "Low").
        :param limit: Number of records to fetch (default is 99999).
        :param sort_column: Column to sort by (default is "symbol").
        :param sort_order: "ASC" or "DESC" (default is "ASC").
        :return: JSON response or None if the request fails.
        """
        params = {
            "queryString": f"exchange={exchange}|status={status}",
            "limit": limit,
            "sortColumn": sort_column,
            "sortOrder": sort_order
        }
        return self.fetch_data("quote/list-type/FIFTYTWOWEEKHILOW", params)

    def fetch_latest_news(self, offset=0, limit=20):
        """
        Fetches the latest news from Nasdaq.

        :param offset: The starting point for fetching news (default is 0).
        :param limit: Number of news articles to fetch (default is 8).
        :return: JSON response or None if the request fails.
        """
        params = {"offset": offset, "limit": limit}
        return self.fetch_data("news/topic/latestnews", params)

    def fetch_trending_articles(self, topic="all"):
        """
        Fetches trending articles from Nasdaq.

        :param topic: The category of articles to fetch (default is 'all').
        :return: JSON response or None if the request fails.
        """
        params = {"topic": topic}
        return self.fetch_data("ga/trending-articles", params)


if __name__ == "__main__":
    nasdaq_api = NasdaqAPI()
    # data = nasdaq_api.get_52_week_high_low(status="Hi", exchange="14")
    # print(data)
    # total_returns = nasdaq_api.indices_total_returns()
    # print(total_returns)
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
    # latest_news = nasdaq_api.fetch_latest_news()
    # print(latest_news)
    trending_articles = nasdaq_api.fetch_trending_articles()
    print(trending_articles)
