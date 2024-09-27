import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from scipy.signal import savgol_filter


def fit_trendlines_single(data: np.array):
    x = np.arange(len(data)).reshape(-1, 1)
    model = LinearRegression().fit(x, data)
    return model.coef_[0], model.intercept_


def remove_outliers(data, n_sigmas=3):
    return data[np.abs(data - np.mean(data)) <= n_sigmas * np.std(data)]


def calculate_trendlines(data: pd.DataFrame, lookback=30, smoothing_window=5, smoothing_poly=2):
    required_columns = ['high', 'low', 'close']
    for col in required_columns:
        if col not in data.columns:
            raise KeyError(f"Column '{col}' is missing from the data.")

    log_data = np.log(data[required_columns].replace(0, np.nan))

    support_levels = np.full(len(data), np.nan)
    resist_levels = np.full(len(data), np.nan)

    for i in range(lookback, len(data)):
        candles = log_data.iloc[i - lookback + 1: i + 1]

        high_clean = remove_outliers(candles['high'].dropna())
        low_clean = remove_outliers(candles['low'].dropna())

        if len(high_clean) < lookback / 2 or len(low_clean) < lookback / 2:
            continue

        try:
            support_slope, support_intercept = fit_trendlines_single(low_clean)
            resist_slope, resist_intercept = fit_trendlines_single(high_clean)

            support_levels[i] = support_slope * lookback + support_intercept
            resist_levels[i] = resist_slope * lookback + resist_intercept

        except Exception as e:
            print(f"Error fitting trendlines for index {i}: {e}")

    # Apply smoothing only to non-NaN values
    valid_indices = ~np.isnan(support_levels)
    support_levels[valid_indices] = savgol_filter(support_levels[valid_indices], smoothing_window, smoothing_poly)
    resist_levels[valid_indices] = savgol_filter(resist_levels[valid_indices], smoothing_window, smoothing_poly)

    # Convert back to price level
    data['support'] = np.exp(support_levels)
    data['resistance'] = np.exp(resist_levels)

    return data[['support', 'resistance']]