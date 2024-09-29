import pandas as pd

def calculate_vwap(data: pd.DataFrame) -> pd.Series:
    """
    Calculate the Volume Weighted Average Price (VWAP).

    Parameters:
    data (pd.DataFrame): A DataFrame containing 'close' and 'volume' columns.

    Returns:
    pd.Series: A Series containing the VWAP values.
    """
    if 'close' not in data.columns or 'volume' not in data.columns:
        raise ValueError("DataFrame must contain 'close' and 'volume' columns")

    vwap = (data['close'] * data['volume']).cumsum() / data['volume'].cumsum()
    return vwap


# Example usage:
if __name__ == "__main__":
    # Sample data for testing
    data = {
        'Close': [100, 102, 101, 105, 103],
        'Volume': [200, 220, 250, 300, 280]
    }
    df = pd.DataFrame(data)

    # Calculate and print VWAP
    vwap_values = calculate_vwap(df)
    print("VWAP Values:")
    print(vwap_values)
