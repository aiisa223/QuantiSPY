import pandas as pd


def calculate_vwap_with_bands_and_signals(input_csv, vwap_period, band_multiplier):
    """
    Calculate VWAP, its bands, and buy signals from CSV file.

    Parameters:
    - input_csv (str): Path to the input CSV file containing historical stock data.
    - vwap_period (int): The VWAP period (number of bars).
    - band_multiplier (float): Multiplier for calculating upper and lower bands.
    """
    # Load CSV data
    df = pd.read_csv(input_csv, parse_dates=True, index_col="Date")

    # Ensure necessary columns exist
    required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    if not all(column in df.columns for column in required_columns):
        raise ValueError("CSV must contain 'Open', 'High', 'Low', 'Close', 'Volume' columns.")

    # Calculate VWAP
    df['typical_price'] = (df['High'] + df['Low'] + df['Close']) / 3
    df['vwap'] = (df['typical_price'] * df['Volume']).cumsum() / df['Volume'].cumsum()

    # Calculate moving average of VWAP for bands
    df['vwap_sma'] = df['vwap'].rolling(window=vwap_period).mean()
    df['vwap_std'] = df['vwap'].rolling(window=vwap_period).std()

    df['upper_band'] = df['vwap_sma'] + (band_multiplier * df['vwap_std'])
    df['lower_band'] = df['vwap_sma'] - (band_multiplier * df['vwap_std'])

    # Generate buy signals
    df['buy_signal'] = ((df['Close'].shift(1) < df['vwap'].shift(1)) & (df['Close'] > df['vwap'])).astype(int)

    # Output the VWAP, bands, and buy signals data
    output_csv = input_csv.replace(".csv", "_vwap_bands_signals.csv")
    df.to_csv(output_csv, index=True)

    print(f"VWAP, bands, and buy signals calculation complete. Output saved to {output_csv}")


# Example usage
if __name__ == "__main__":
    calculate_vwap_with_bands_and_signals("spy_data/spy_data_5m.csv", vwap_period=20, band_multiplier=1)
