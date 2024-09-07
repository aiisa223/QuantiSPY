import requests
import pandas as pd
from datetime import datetime
import os

API_KEY = 'o1jQl2lXxGwwzVgxxrH97fNUUbqHp3NM'

def ensure_directory_exists(file_path):
    """Ensure the directory for the file exists, and create it if not."""
    directory = os.path.dirname(file_path)

    # Only create a directory if the path is not empty
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Directory {directory} created.")

def fetch_spy_data_for_today(output_csv):
    """Fetch daily SPY data for the current day from Polygon.io and save to a CSV."""
    print("Starting SPY data fetch for today...")

    # Ensure the directory for the output file exists
    ensure_directory_exists(output_csv)

    # Get today's date in the required format (YYYY-MM-DD)
    today = datetime.today().strftime('%Y-%m-%d')

    # Polygon.io URL for daily interval data
    url = f'https://api.polygon.io/v2/aggs/ticker/SPY/range/1/day/{today}/{today}'

    params = {
        'apiKey': API_KEY
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if 'results' not in data or not data['results']:
            raise ValueError("No data returned for today.")

        # Convert data to DataFrame
        df = pd.DataFrame(data['results'])
        df['timestamp'] = pd.to_datetime(df['t'], unit='ms')
        df.set_index('timestamp', inplace=True)
        df.drop(columns=['t'], inplace=True)

        # Save DataFrame to CSV
        df.to_csv(output_csv)
        print(f"SPY daily data for today saved to {output_csv}")

    except Exception as e:
        print(f"Error fetching SPY data: {e}")

# Example usage
if __name__ == "__main__":
    output_csv = "spy_data_today_1d.csv"
    fetch_spy_data_for_today(output_csv)