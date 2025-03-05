import requests

calendar_url = "https://api.nasdaq.com/api/calendar/earnings?date=2025-03-04"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nasdaq.com/",
    "Connection": "keep-alive"
}

if __name__ == "__main__":
    response = requests.get(calendar_url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(data)
    else:
        print(f"Request failed with status code {response.status_code}")
