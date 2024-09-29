import pandas as pd
import numpy as np
from typing import Optional


def calculate_relative_strength(stock_data: pd.DataFrame, spy_data: pd.DataFrame, lookback_periods: int = 12) -> \
Optional[float]:
    try:
        # Ensure the data is aligned and has the same length
        common_index = stock_data.index.intersection(spy_data.index)
        stock_data = stock_data.loc[common_index]
        spy_data = spy_data.loc[common_index]

        if stock_data.empty or spy_data.empty:
            print("Error: No common data between stock and SPY")
            return None

        # Calculate returns
        stock_returns = stock_data['close'].pct_change().fillna(0)
        spy_returns = spy_data['close'].pct_change().fillna(0)

        # Calculate ATR for both stock and SPY
        stock_atr = calculate_atr(stock_data, lookback_periods)
        spy_atr = calculate_atr(spy_data, lookback_periods)

        if stock_atr == 0 or spy_atr == 0:
            print("Error: ATR calculation resulted in zero")
            return None

        # Calculate volume-weighted returns
        stock_volume_weighted_returns = stock_returns * stock_data['volume']
        spy_volume_weighted_returns = spy_returns * spy_data['volume']

        # Calculate Relative Strength
        rs_raw = (stock_returns.tail(lookback_periods).mean() / stock_atr) - (
                    spy_returns.tail(lookback_periods).mean() / spy_atr)
        rs_volume_weighted = (stock_volume_weighted_returns.tail(lookback_periods).mean() / stock_atr) - (
                    spy_volume_weighted_returns.tail(lookback_periods).mean() / spy_atr)

        # Combine raw and volume-weighted Relative Strength
        relative_strength = (rs_raw + rs_volume_weighted) / 2

        return float(relative_strength)
    except Exception as e:
        print(f"Error calculating relative strength: {str(e)}")
        return None


def calculate_atr(data: pd.DataFrame, lookback_periods: int = 14) -> float:
    high = data['high']
    low = data['low']
    close = data['close']

    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())

    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=lookback_periods).mean().iloc[-1]

    return float(atr)
