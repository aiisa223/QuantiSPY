import pandas as pd
import mplfinance as mpf
import os

def plot_data_with_signals(csv_file):
    try:
        # Check if file exists
        if not os.path.exists(csv_file):
            raise FileNotFoundError(f"File not found: {csv_file}")

        # Load the data from the CSV
        df = pd.read_csv(csv_file, parse_dates=True, index_col="Date")

        if df.empty:
            print("No data to plot.")
            return

        # Ensure data columns are named correctly for mplfinance
        df.rename(columns={
            'Open': 'Open',
            'High': 'High',
            'Low': 'Low',
            'Close': 'Close',
            'Volume': 'Volume'
        }, inplace=True)

        # Ensure the index is properly set to 'Date'
        df.index.name = 'Date'

        # Create additional plot elements for VWAP, bands, and buy signals
        apds = []

        # VWAP
        if 'vwap' in df.columns:
            if len(df) == len(df['vwap']):
                apds.append(mpf.make_addplot(df['vwap'], color='blue', linestyle='--'))

        # Bands
        if 'upper_band' in df.columns and 'lower_band' in df.columns:
            if len(df) == len(df['upper_band']) == len(df['lower_band']):
                apds.append(mpf.make_addplot(df['upper_band'], color='red', linestyle='--'))
                apds.append(mpf.make_addplot(df['lower_band'], color='green', linestyle='--'))

        # Buy signals
        if 'buy_signal' in df.columns:
            buy_signals = df[df['buy_signal'] == 1]
            if not buy_signals.empty:
                # Ensure buy_signals indices align with df index
                buy_signals = buy_signals.reindex(df.index)
                if len(df) == len(buy_signals):
                    apds.append(mpf.make_addplot(buy_signals['Close'], type='scatter', markersize=100, color='magenta'))

        # Plotting data using mplfinance
        mpf.plot(df, type='candle', style='charles', title='SPY 5-Minute Interval Candlestick Chart',
                 ylabel='Price', volume=True, addplot=apds)

    except Exception as e:
        print(f"Error plotting data. Something went wrong: {e}")

# Example usage
if __name__ == '__gui__':
    plot_data_with_signals("spy_data/spy_data_5m_vwap_bands_signals.csv")  # Update with the path to your CSV file
