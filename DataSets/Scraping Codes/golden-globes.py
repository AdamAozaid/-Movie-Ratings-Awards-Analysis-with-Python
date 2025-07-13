import requests
from bs4 import BeautifulSoup
import pandas as pd

# Wikipedia page URL
url = "https://en.wikipedia.org/wiki/List_of_Golden_Globe_winners"

# Send the HTTP request
response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")

# Find all wikitable elements
tables = soup.find_all("table", class_="wikitable")

# Define standard columns
standard_columns = [
    "Year", "Best Picture", "Best Actor", "Best Actress", "Director",
    "Drama Actor", "Musical/Comedy Actor", "Drama Actress",
    "Musical/Comedy Actress", "Drama", "Musical/Comedy"
]

# Initialize list to hold all rows from all tables
all_tables_data = []

# Loop through each table
for index, table in enumerate(tables):
    try:
        df = pd.read_html(str(table))[0]
        df.columns = [str(col).strip() for col in df.columns]  # Clean column names
        df.insert(0, "Source_Table", f"{index + 1}")  # Just the table number

        # Add missing columns
        for col in standard_columns:
            if col not in df.columns:
                df[col] = pd.NA

        # Reorder columns
        ordered_columns = ["Source_Table", "Year"] + standard_columns[1:]
        df = df[ordered_columns]

        all_tables_data.append(df)
    except Exception as e:
        print(f"⚠️ Skipping table {index + 1}: {e}")

# Combine all tables
combined_df = pd.concat(all_tables_data, ignore_index=True)

# Save to CSV
combined_df.to_csv("golden_globes.csv", index=False)
print("✅ Structured CSV saved as 'golden_globe_all_tables_structured.csv'")
