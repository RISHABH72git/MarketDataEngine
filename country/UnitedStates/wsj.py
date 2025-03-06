import requests


class WSJAPI:
    BASE_URL = "https://www.wsj.com/market-data/stocks"

    def __init__(self, user_agent=None):
        """Initialize headers with required values."""
        self.headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-GB,en;q=0.7",
            "Referer": "https://www.wsj.com/market-data/stocks/newfiftytwoweekhighsandlows",
            "Sec-CH-UA": '"Chromium";v="134", "Not:A-Brand";v="24", "Brave";v="134"',
            "Sec-CH-UA-Arch": '"x86"',
            "Sec-CH-UA-Full-Version-List": '"Chromium";v="134.0.0.0", "Not:A-Brand";v="24.0.0.0", "Brave";v="134.0.0.0"',
            "Sec-CH-UA-Mobile": "?0",
            "Sec-CH-UA-Model": '""',
            "Sec-CH-UA-Platform": '"Linux"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Sec-GPC": "1",
            "User-Agent": user_agent or "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
                                        "Chrome/134.0.0.0 Safari/537.36"
        }

    def fetch_52_week_high_low(self):
        """Fetch 52-week high and low stocks."""
        endpoint = "newfiftytwoweekhighsandlows"
        params = {
            "id": '{"application":"WSJ","refreshInterval":300000}',
            "type": "mdc_fiftytwoweek"
        }
        url = f"{self.BASE_URL}/{endpoint}"
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()  # Raise an error for 4xx and 5xx responses
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching WSJ data: {e}")
            return None


if __name__ == "__main__":
    wsj_api = WSJAPI()
    high_low_data = wsj_api.fetch_52_week_high_low()
    print(high_low_data)
