import requests
import time


class NSEAPI:
    BASE_URL = "https://www.nseindia.com/api"

    def __init__(self):
        self.session = requests.Session()
        self._set_headers()
        self._initialize_session()

    def _set_headers(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.nseindia.com/",
            "Connection": "keep-alive",
            "Host": "www.nseindia.com"
        }
        self.session.headers.update(self.headers)

    def _initialize_session(self):
        """Visit NSE homepage to establish cookies and bypass protection."""
        try:
            print("Initializing session...")
            self.session.get("https://www.nseindia.com", timeout=10)
            time.sleep(3)  # Increased delay to allow all protections to pass
            print("Session initialized successfully.")
        except requests.RequestException as e:
            print(f"Failed to initialize session: {e}")

    def _fetch_data(self, endpoint, params=None):
        """Fetch data from NSE API endpoint with retry mechanism."""
        url = f"{self.BASE_URL}/{endpoint}"
        try:
            response = self.session.get(url, params=params, headers=self.headers, timeout=10)

            if response.status_code == 401 or "html" in response.text.lower():
                print("Unauthorized access or blocked, refreshing session...")
                self._initialize_session()
                time.sleep(5)  # Wait for session to stabilize
                response = self.session.get(url, params=params, headers=self.headers, timeout=10)

            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching NSE data: {e}")
            return None

    def get_market_status(self):
        """Fetch market status from NSE."""
        return self._fetch_data("marketStatus")

    def get_high_low_count(self):
        """Fetch NSE 52-week high low count."""
        return self._fetch_data("live-analysis-52weekhighstock")

    def get_fifty_two_week_low_data(self):
        """Fetch NSE 52-week low data."""
        return self._fetch_data("live-analysis-data-52weeklowstock")

    def get_fifty_two_week_high_data(self):
        """Fetch NSE 52-week high data."""
        return self._fetch_data("live-analysis-data-52weekhighstock")

    def get_event_calendar(self, start_date, end_date):
        """Fetch NSE event calendar."""
        return self._fetch_data("event-calendar",
                                params={"index": "equities", "from_date": start_date, "to_date": end_date})

    def index_performances(self):
        """Fetch NSE index data."""
        return self._fetch_data("allIndices")


# Usage
if __name__ == "__main__":
    nse_api = NSEAPI()

    # Fetch market status
    market_status = nse_api.get_market_status()
    print("Market Status:", market_status)

    # Fetch high-low count
    high_low_count = nse_api.get_high_low_count()
    print(high_low_count)

    # Fetch 52-week high data
    high_data = nse_api.get_fifty_two_week_high_data()
    print(high_data)

    # Fetch 52-week low data
    low_data = nse_api.get_fifty_two_week_low_data()
    print(low_data)

    # Fetch event calendar
    event_calendar = nse_api.get_event_calendar(start_date="06-03-2025", end_date="06-03-2025")
    print(event_calendar)

    # Fetch index performances
    index_performance = nse_api.index_performances()
    print(index_performance)
