import time
import random
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
import undetected_chromedriver as uc


class WebDriverManager:
    def __init__(self):
        self.driver = None

    def start_driver(self):
        options = uc.ChromeOptions()
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--incognito')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument("--window-size=1920,1080")
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/91.0.4472.101 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Version/14.0.3 Safari/605.1.15"
        ]
        options.add_argument(f'user-agent={random.choice(user_agents)}')

        self.driver = uc.Chrome(options=options, headless=True)

    def get_driver(self):
        if not self.driver:
            self.start_driver()
        return self.driver

    def close_driver(self):
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
            self.driver = None


class EarningsCalendarParser:
    def __init__(self, html: str):
        self.soup = BeautifulSoup(html, 'html.parser')

    def parse(self) -> pd.DataFrame:
        table = self.soup.find('table', {'id': 'earningsCalendarData'})
        if not table:
            print("Earnings calendar table not found.")
            return pd.DataFrame()

        rows = table.find('tbody').find_all('tr')
        data = []

        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 8:
                eps_forecast = cells[3].get_text(strip=True)
                revenue_forecast = cells[5].get_text(strip=True)

                # Clean up forecast fields
                eps_forecast = eps_forecast.replace('/', '') if "/" in eps_forecast else eps_forecast
                revenue_forecast = revenue_forecast.replace('/', '') if "/" in revenue_forecast else revenue_forecast

                data.append({
                    'Company': cells[1].get_text(strip=True),
                    'EPS': cells[2].get_text(strip=True),
                    'EPS Forecast': eps_forecast,
                    'Revenue': cells[4].get_text(strip=True),
                    'Revenue Forecast': revenue_forecast,
                    'Market Cap': cells[6].get_text(strip=True),
                    'Time': cells[7].get_text(strip=True),
                })

        return pd.DataFrame(data)


class EarningsCalendarScraper:
    def __init__(self, url: str, retry_interval: int = 5):
        self.url = url
        self.retry_interval = retry_interval
        self.driver_manager = WebDriverManager()

    def run(self):
        attempt = 0
        while True:
            try:
                print(f"[{datetime.now()}]  Starting scraping attempt {attempt + 1}")
                self.driver_manager.start_driver()
                driver = self.driver_manager.get_driver()
                driver.get(self.url)

                time.sleep(random.uniform(5, 7))  # Random delay to simulate human behavior

                if "Just a moment..." in driver.title or "Checking your browser" in driver.page_source:
                    raise Exception("Cloudflare challenge detected")

                html = driver.page_source
                parser = EarningsCalendarParser(html)
                df = parser.parse()

                if df.empty:
                    print(" No data extracted.")
                else:
                    print(f"[{datetime.now()}] Successfully extracted {len(df)} rows.")
                    print(df.head())
                    return df

            except Exception as e:
                print(f"[{datetime.now()}] Error during scraping: {e}")
                attempt += 1
                time.sleep(min(60, self.retry_interval * attempt))
            finally:
                self.driver_manager.close_driver()


if __name__ == "__main__":
    url = "https://www.investing.com/earnings-calendar/"
    scraper = EarningsCalendarScraper(url)
    earnings_df = scraper.run()
