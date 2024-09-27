import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D
from matplotlib.widgets import MultiCursor
from directional_change import directional_change
from trendline import calculate_trendlines
import mplcursors

plt.style.use('dark_background')


def plot_candlestick(ax, df):
    print("Plotting candlesticks...")
    df = df.copy()
    df['date_num'] = np.arange(len(df))

    width = 0.8

    up = df[df.close >= df.open]
    down = df[df.close < df.open]

    # Increase contrast for candlesticks
    up_color = '#00ff00'  # Bright green
    down_color = '#ff0000'  # Bright red

    # Plot up candlesticks
    ax.bar(up.date_num, up.close - up.open, width, bottom=up.open, color=up_color, edgecolor=up_color, linewidth=1,
           zorder=3)
    ax.vlines(up.date_num, up.low, up.high, color=up_color, linewidth=1, zorder=2)

    # Plot down candlesticks
    ax.bar(down.date_num, down.close - down.open, width, bottom=down.open, color=down_color, edgecolor=down_color,
           linewidth=1, zorder=3)
    ax.vlines(down.date_num, down.low, down.high, color=down_color, linewidth=1, zorder=2)

    ax.set_xlim(-1, len(df))
    ax.set_ylim(df.low.min() * 0.999, df.high.max() * 1.001)

    print(f"Plotted {len(df)} candlesticks.")


def plot_volume(ax, df):
    print("Plotting volume...")
    df = df.copy()
    df['date_num'] = np.arange(len(df))

    width = 0.8
    up = df[df.close >= df.open]
    down = df[df.close < df.open]

    # Increase contrast for volume bars
    ax.bar(up.date_num, up.volume, width, color='#00ff00', alpha=0.5)
    ax.bar(down.date_num, down.volume, width, color='#ff0000', alpha=0.5)

    ax.set_xlim(-1, len(df))
    ax.set_ylim(0, df.volume.max() * 1.5)

    # Format y-axis to show volume in millions
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x / 1e6:.1f}M'))

    print("Volume plotted.")


def plot_directional_change(ax, dc_df, marker_size=50):
    print("Plotting directional changes...")
    dc_df = dc_df.copy()
    dc_df['date_num'] = dc_df.index.map(dict(zip(dc_df.index, range(len(dc_df)))))

    mask = (dc_df['bullish'] == 1) | (dc_df['bearish'] == 1)
    indices = dc_df.loc[mask, 'date_num']
    prices = dc_df.loc[mask, 'close']
    colors = ['#00ff00' if bull else '#ff0000' for bull in dc_df.loc[mask, 'bullish']]

    for i in range(len(indices) - 1):
        ax.plot(indices.iloc[i:i + 2], prices.iloc[i:i + 2], color=colors[i], linewidth=2, alpha=0.7)

    ax.scatter(indices, prices, c=colors, s=marker_size, zorder=5, alpha=0.7)

    print(f"Plotted zig-zag line with {len(indices)} turning points.")


def plot_trendlines(ax, df):
    print("Plotting trendlines...")
    df = df.copy()
    df['date_num'] = np.arange(len(df))
    valid_data = df.dropna(subset=['support', 'resistance'])
    ax.plot(valid_data['date_num'], valid_data['support'], color='#2962ff', linestyle='--', linewidth=2, alpha=0.7)
    ax.plot(valid_data['date_num'], valid_data['resistance'], color='#ff6d00', linestyle='--', linewidth=2, alpha=0.7)
    print("Trendlines plotted.")


def plot_stock_data(fig, df, ticker, sigma=0.005, min_change=0.002, window=3, min_duration=2):
    # Create subplots with shared x-axis
    gs = fig.add_gridspec(2, 1, height_ratios=[3, 1], hspace=0)
    ax1 = fig.add_subplot(gs[0])
    ax2 = fig.add_subplot(gs[1], sharex=ax1)

    plot_candlestick(ax1, df)
    plot_volume(ax2, df)

    dc_df = directional_change(df['high'], df['low'], df['close'], sigma=sigma, min_change=min_change, window=window,
                               min_duration=min_duration)
    plot_directional_change(ax1, dc_df)

    trendline_df = calculate_trendlines(df, lookback=12, smoothing_window=3, smoothing_poly=2)
    plot_trendlines(ax1, trendline_df)

    ax1.set_title(f'{ticker} Stock Price (5-min) with Directional Changes and Trendlines', color='white',
                  fontweight='bold', fontsize=16)
    ax1.set_ylabel('Price ($)', color='white', fontsize=12)
    ax2.set_xlabel('Time', color='white', fontsize=12)
    ax2.set_ylabel('Volume', color='white', fontsize=12)

    for ax in [ax1, ax2]:
        ax.grid(True, linestyle='--', alpha=0.3, color='gray')
        ax.set_axisbelow(True)

    # Improve x-axis labels
    num_ticks = 8
    tick_locations = np.linspace(0, len(df) - 1, num_ticks, dtype=int)
    ax2.set_xticks(tick_locations)
    ax2.set_xticklabels(df.index[tick_locations].strftime('%I:%M %p'), rotation=45, ha='right', color='white')

    # Improve y-axis labels
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"${x:.2f}"))
    ax1.tick_params(axis='y', colors='white', labelsize=10)
    ax2.tick_params(axis='y', colors='white', labelsize=10)

    custom_lines = [Line2D([0], [0], color='#00ff00', lw=2),
                    Line2D([0], [0], color='#ff0000', lw=2),
                    Line2D([0], [0], color='#2962ff', linestyle='--', lw=2),
                    Line2D([0], [0], color='#ff6d00', linestyle='--', lw=2)]
    ax1.legend(custom_lines, ['Bullish Trend', 'Bearish Trend', 'Support', 'Resistance'],
               loc='upper left', facecolor='#1e1e1e', edgecolor='white', framealpha=0.8, fontsize=10)

    for ax in [ax1, ax2]:
        ax.set_facecolor('#1e1e1e')
    fig.set_facecolor('#1e1e1e')

    # Enable zooming and panning
    fig.canvas.mpl_connect('scroll_event', lambda event: on_scroll(event, ax1, ax2))
    fig.canvas.mpl_connect('button_press_event', lambda event: on_press(event, fig, ax1, ax2))
    fig.canvas.mpl_connect('button_release_event', lambda event: on_release(event, fig))
    fig.canvas.mpl_connect('motion_notify_event', lambda event: on_motion(event, fig, ax1, ax2))

    # Add cursor
    multi = MultiCursor(fig.canvas, (ax1, ax2), color='white', lw=1, horizOn=True, vertOn=True)

    # Add tooltips
    cursor = mplcursors.cursor(hover=True)
    cursor.connect("add", lambda sel: sel.annotation.set_text(
        f'Time: {df.index[int(sel.target.index)].strftime("%Y-%m-%d %H:%M")}\n'
        f'Open: ${df.iloc[int(sel.target.index)].open:.2f}\n'
        f'High: ${df.iloc[int(sel.target.index)].high:.2f}\n'
        f'Low: ${df.iloc[int(sel.target.index)].low:.2f}\n'
        f'Close: ${df.iloc[int(sel.target.index)].close:.2f}\n'
        f'Volume: {df.iloc[int(sel.target.index)].volume:,}'
    ))

    plt.tight_layout()


def on_scroll(event, ax1, ax2):
    base_scale = 1.1
    # zoom in
    if event.button == 'up':
        scale_factor = 1 / base_scale
    # zoom out
    else:
        scale_factor = base_scale

    for ax in [ax1, ax2]:
        x_min, x_max = ax.get_xlim()
        y_min, y_max = ax.get_ylim()

        x_center = x_min + (x_max - x_min) / 2
        y_center = y_min + (y_max - y_min) / 2

        ax.set_xlim([x_center - (x_center - x_min) * scale_factor,
                     x_center + (x_max - x_center) * scale_factor])
        ax.set_ylim([y_center - (y_center - y_min) * scale_factor,
                     y_center + (y_max - y_center) * scale_factor])

    event.canvas.draw()


def on_press(event, fig, ax1, ax2):
    fig._pan_start = (ax1.get_xlim(), ax1.get_ylim(), ax2.get_ylim(), event.x, event.y)


def on_release(event, fig):
    fig._pan_start = None


def on_motion(event, fig, ax1, ax2):
    if fig._pan_start is None or event.button != 1:  # Left mouse button
        return

    dx = event.x - fig._pan_start[3]
    dy = event.y - fig._pan_start[4]

    x_min, x_max = fig._pan_start[0]
    y1_min, y1_max = fig._pan_start[1]
    y2_min, y2_max = fig._pan_start[2]

    scale_x = (x_max - x_min) / fig.get_figwidth()
    scale_y1 = (y1_max - y1_min) / fig.get_figheight()
    scale_y2 = (y2_max - y2_min) / fig.get_figheight()

    ax1.set_xlim(x_min - dx * scale_x, x_max - dx * scale_x)
    ax1.set_ylim(y1_min + dy * scale_y1, y1_max + dy * scale_y1)
    ax2.set_ylim(y2_min + dy * scale_y2, y2_max + dy * scale_y2)

    fig.canvas.draw()