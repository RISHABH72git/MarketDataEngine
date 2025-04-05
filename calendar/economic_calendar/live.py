import random
import time
from datetime import datetime

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver


class ValueExtractor:
    @staticmethod
    def extract_value_and_unit(value: str):
        if value and value[-1] in ['M', 'K', 'B', '%', 'T']:
            return value[:-1], value[-1]
        return value, None


class EconomicEventParser:
    IMPORTANCE_MAPPING = {
        "High Volatility Expected": 4,
        "Moderate Volatility Expected": 3,
        "Low Volatility Expected": 2
    }

    def __init__(self, page_source: str):
        self.soup = BeautifulSoup(page_source, 'html.parser')

    def parse(self):
        table = self.soup.find('table', {'id': 'ecEventsTable'})
        data = []
        if not table:
            return pd.DataFrame()

        for tr in table.find_all('tr'):
            cells = tr.find_all('td')
            if not cells or len(cells) < 7:
                continue

            imp_td = cells[2]
            imp_text = imp_td.get('title', None)
            imp_value = self.IMPORTANCE_MAPPING.get(imp_text, 0)

            country_span = tr.find('span', class_='ceFlags')
            country_name = country_span['title'] if country_span else 'Unknown'

            actual_value, actual_unit = ValueExtractor.extract_value_and_unit(cells[4].get_text(strip=True))
            forecast_value, forecast_unit = ValueExtractor.extract_value_and_unit(cells[5].get_text(strip=True))
            previous_value, previous_unit = ValueExtractor.extract_value_and_unit(cells[6].get_text(strip=True))

            units = [actual_unit, forecast_unit, previous_unit]
            final_unit = next((u for u in units if u), "")

            date_time_str = tr.get('event_timestamp')
            event_name = cells[3].get_text(strip=True)
            event_url = f"{tr.get('id')}_{tr.get('event_attr_id')}_{event_name.replace(' ', '_')}"

            data.append({
                "currency": cells[1].get_text(strip=True),
                "event": event_name,
                "actual": actual_value,
                "forecast": forecast_value,
                "previous": previous_value,
                "impact": imp_value,
                "country": country_name,
                "date": date_time_str,
                "url": event_url,
                "unit": final_unit
            })

        return pd.DataFrame(data)


class WebDriverManager:
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15'
    ]

    def __init__(self):
        self.driver = None

    def start_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--incognito')
        options.add_argument('--disable-background-timer-throttling')
        options.add_argument('--disable-backgrounding-occluded-windows')
        options.add_argument('--disable-renderer-backgrounding')
        options.add_argument(f'user-agent={random.choice(self.USER_AGENTS)}')
        self.driver = webdriver.Chrome(options=options)

    def get_driver(self):
        if not self.driver:
            self.start_driver()
        return self.driver

    def close_driver(self):
        if self.driver:
            self.driver.quit()
            self.driver = None


class EconomicCalendarScraper:
    def __init__(self, url: str, interval: int = 5):
        self.url = url
        self.driver_manager = WebDriverManager()
        self.previous_df = pd.DataFrame()
        self.interval = interval

    def run(self):
        retry_count = 0
        while True:
            try:
                print(f"[{datetime.now()}] Starting scraper (attempt {retry_count + 1})")
                self.driver_manager.start_driver()
                driver = self.driver_manager.get_driver()
                driver.get(self.url)
                time.sleep(3)  # Give it time to load

                while True:
                    self._scrape(driver)
                    time.sleep(self.interval)

            except Exception as e:
                print(f"[{datetime.now()}] Error occurred: {e}")
                self.driver_manager.close_driver()
                retry_count += 1
                wait_time = min(60, retry_count * 5)  # exponential backoff (up to 60s)
                print(f"[{datetime.now()}] Restarting in {wait_time} seconds...\n")
                time.sleep(wait_time)

            finally:
                self.driver_manager.close_driver()

    def _scrape(self, driver):
        parser = EconomicEventParser(driver.page_source)
        current_df = parser.parse()

        if current_df.empty:
            return

        if not self.previous_df.empty:
            current_df_reindexed = current_df.reindex_like(self.previous_df)
            updated_rows = self.previous_df.compare(current_df_reindexed, keep_shape=True, keep_equal=False)
            updated_indices = updated_rows.dropna(how='all').index
            updated_data = current_df_reindexed.loc[updated_indices]

            # New events
            if len(current_df) > len(self.previous_df):
                diff_df = current_df[~current_df.apply(tuple, 1).isin(self.previous_df.apply(tuple, 1))]
                updated_data = pd.concat([updated_data, diff_df], ignore_index=True)

            if not updated_data.empty:
                updated_data = updated_data.drop_duplicates()
                print(f"Updated data:\n{len(updated_data)}")

        self.previous_df = current_df


if __name__ == "__main__":
    url = 'https://sslecal2.investing.com/'
    scraper = EconomicCalendarScraper(url)
    scraper.run()
