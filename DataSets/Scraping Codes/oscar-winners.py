import requests
from bs4 import BeautifulSoup
import csv

session = requests.Session()
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'Accept-Language': 'en-US,en;q=0.9',
}
session.headers.update(headers)

# URLs
urls = {
    "Best Picture": "https://www.britannica.com/art/Academy-Award-for-best-picture",
    "Best Actor": "https://www.britannica.com/art/Academy-Award-for-best-actor",
    "Best Actress": "https://www.britannica.com/art/Academy-Award-for-best-actress",
}

# Scrape data into {year: {"Best Picture": ..., "Best Actor": ..., ...}}
award_data = {}

def scrape_award(url, category):
    response = session.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch: {url}")
        return

    soup = BeautifulSoup(response.text, "html.parser")
    items = soup.select("section ul li")

    for item in items:
        text = item.get_text(strip=True)
        if ":" in text:
            year, value = text.split(":", 1)
            year = year.strip()
            value = value.strip()
        else:
            year = "N/A"
            value = text.strip()
        
        if year not in award_data:
            award_data[year] = {}
        award_data[year][category] = value

# Scrape each award category
for category, url in urls.items():
    scrape_award(url, category)

# Save to single CSV
with open("oscars_awards.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Year", "Best Picture", "Best Actor", "Best Actress"])

    for year in sorted(award_data.keys()):
        row = [
            year,
            award_data[year].get("Best Picture", "N/A"),
            award_data[year].get("Best Actor", "N/A"),
            award_data[year].get("Best Actress", "N/A"),
        ]
        writer.writerow(row)
