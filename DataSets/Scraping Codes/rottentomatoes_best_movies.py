import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

session = requests.Session()
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'Accept-Language': 'en-US,en;q=0.9',
}
session.headers.update(headers)

BASE_URL = "https://editorial.rottentomatoes.com"

def get_movie_info(movie_url):
    response = session.get(movie_url)
    if response.status_code != 200:
        return ["N/A"] * 7

    soup = BeautifulSoup(response.text, "html.parser")

    # Metadata: Parents Guide, Release Date, Duration
    metadata = soup.find_all("rt-text", {"slot": "metadataProp", "context": "label"})
    metadata_values = [tag.text.strip().replace('\xa0', ' ') for tag in metadata]
    parents_guide = metadata_values[0] if len(metadata_values) > 0 else "N/A"
    release_date = metadata_values[1] if len(metadata_values) > 1 else "N/A"
    duration = metadata_values[2] if len(metadata_values) > 2 else "N/A"

    # Genre
    genre_tags = soup.find_all("rt-text", {"slot": "metadataGenre"})
    genre = ", ".join([tag.text.strip().strip("/") for tag in genre_tags]) if genre_tags else "N/A"

    # Director, Producer, Box Office
    media_metadata = soup.find_all("rt-link", {"data-qa": "item-value"})
    media_metadata = [tag.text.strip().replace('\xa0', ' ') for tag in media_metadata]
    director = media_metadata[0] if len(media_metadata) > 0 else "N/A"
    producer = media_metadata[1] if len(media_metadata) > 1 else "N/A"
    box_office = media_metadata[2] if len(media_metadata) > 2 else "N/A"

    return [parents_guide, release_date, duration, genre, director, producer, box_office]

def main(url):
    response = session.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch: {url}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    containers = soup.find_all("p", class_="apple-news-link-wrap movie")
    print(f"Found {len(containers)} movies on this page")

    movies = []

    for item in containers:
        title_tag = item.find("a", class_="title")
        title = title_tag.text.strip() if title_tag else "N/A"
        relative_link = title_tag['href'] if title_tag and 'href' in title_tag.attrs else None
        full_link = relative_link if relative_link.startswith("http") else BASE_URL + relative_link if relative_link else None

        year_tag = item.find("span", class_="year")
        year = year_tag.text.strip("() ") if year_tag else "N/A"

        rating_tag = item.find("span", class_="score")
        rating = rating_tag.text.strip() if rating_tag else "N/A"

        if full_link:
            extra_info = get_movie_info(full_link)
            # time.sleep(1)  # Optional: Be nice to the server
        else:
            extra_info = ["N/A"] * 7  # Ensure 7 fields for alignment

        print(f"{title} - {year} - {rating} - {extra_info}")
        movies.append([title, year, rating] + extra_info)

    # Save to Excel
    df = pd.DataFrame(movies, columns=[
        "Title", "Year", "Rating",
        "Parents Guide", "Release Date", "Duration", "Genre",
        "Director", "Producer", "Box Office"
    ])
    df.to_excel("rottentomatoes_best_movies.xlsx", index=False)
    print(f"\nDone. Total movies scraped: {len(movies)}")
    return movies

main("https://editorial.rottentomatoes.com/guide/best-movies-of-all-time/")
