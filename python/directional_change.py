import pandas as pd
import numpy as np


def directional_change(high, low, close, sigma=0.01, min_change=0.005, window=5, min_duration=3):
    df = pd.DataFrame({'high': high, 'low': low, 'close': close})
    df['rolling_high'] = df['high'].rolling(window=window).max()
    df['rolling_low'] = df['low'].rolling(window=window).min()

    df['price_change'] = df['close'].pct_change(window)

    bullish = [0] * window
    bearish = [0] * window
    tmp_max = df['rolling_high'].iloc[window - 1]
    tmp_min = df['rolling_low'].iloc[window - 1]
    last_signal_price = close.iloc[window - 1]
    trend_duration = 0
    current_trend = 0  # 0 for no trend, 1 for bullish, -1 for bearish

    for i in range(window, len(high)):
        price_change = df['price_change'].iloc[i]

        if df['rolling_high'].iloc[i] > tmp_max and price_change > min_change:
            tmp_max = df['rolling_high'].iloc[i]
            if trend_duration >= min_duration:
                bullish.append(1)
                bearish.append(0)
                last_signal_price = close.iloc[i]
                trend_duration = 0
                current_trend = 1
            else:
                bullish.append(0)
                bearish.append(0)
        elif close.iloc[i] < tmp_max - tmp_max * sigma and price_change < -min_change:
            tmp_max = df['rolling_high'].iloc[i]
            if trend_duration >= min_duration:
                bullish.append(0)
                bearish.append(1)
                last_signal_price = close.iloc[i]
                trend_duration = 0
                current_trend = -1
            else:
                bullish.append(0)
                bearish.append(0)
        else:
            bullish.append(0)
            bearish.append(0)

        if df['rolling_low'].iloc[i] < tmp_min:
            tmp_min = df['rolling_low'].iloc[i]
        elif close.iloc[i] > tmp_min + tmp_min * sigma:
            tmp_min = df['rolling_low'].iloc[i]

        trend_duration += 1

    return pd.DataFrame({
        'close': close,
        'bullish': bullish,
        'bearish': bearish
    })