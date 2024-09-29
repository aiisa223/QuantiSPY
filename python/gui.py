import sys
import os
import numpy as np
import traceback
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox

# Add the Release directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Release')))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stock_hmm  # type: ignore
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from alpha_vantage.timeseries import TimeSeries
import pandas as pd
import yfinance as yf
from python.plotter import plot_stock_data
from PIL import Image, ImageTk
from python.directional_change import directional_change
from python.trendline import calculate_trendlines
import matplotlib.dates as mdates
from python.relativestrength import calculate_relative_strength

class StockAnalyzerGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("QuantiSPY: Instant Technical Analysis")
        self.master.geometry("1000x800")

        self.style = ttk.Style(theme="darkly")

        self.api_var = ttk.StringVar(value="Alpha Vantage")
        self.api_key = ttk.StringVar()
        self.data = None
        self.spy_data = None
        self.hmm = None
        self.num_states = ttk.IntVar(value=3)

        self.create_widgets()

    def create_widgets(self):
        # Logo
        logo_frame = ttk.Frame(self.master)
        logo_frame.pack(pady=10)
        self.load_logo(logo_frame)

        # API Selection
        api_frame = ttk.Frame(self.master)
        api_frame.pack(pady=5)
        ttk.Label(api_frame, text="Select API:").pack(side=LEFT)
        ttk.Radiobutton(api_frame, text="Alpha Vantage", variable=self.api_var, value="Alpha Vantage").pack(side=LEFT)
        ttk.Radiobutton(api_frame, text="Yahoo Finance", variable=self.api_var, value="Yahoo Finance").pack(side=LEFT)

        # API Key Input (for Alpha Vantage)
        key_frame = ttk.Frame(self.master)
        key_frame.pack(pady=5)
        ttk.Label(key_frame, text="Alpha Vantage API Key:").pack(side=LEFT)
        ttk.Entry(key_frame, textvariable=self.api_key, width=40).pack(side=LEFT)

        # Stock Symbol Input
        input_frame = ttk.Frame(self.master)
        input_frame.pack(pady=5)
        ttk.Label(input_frame, text="Enter Stock Symbol:").pack(side=LEFT)
        self.symbol_entry = ttk.Entry(input_frame, width=10)
        self.symbol_entry.pack(side=LEFT)
        ttk.Button(input_frame, text="Analyze", command=self.analyze_stock, style="success.TButton").pack(side=LEFT)

        # HMM Configuration Frame
        hmm_frame = ttk.Labelframe(self.master, text="HMM Configuration")
        hmm_frame.pack(pady=5, padx=10, fill="x")

        ttk.Label(hmm_frame, text="Number of States:").grid(row=0, column=0, padx=5, pady=5)
        ttk.Entry(hmm_frame, textvariable=self.num_states, width=5).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(hmm_frame, text="Apply HMM", command=self.apply_hmm_analysis, style="info.TButton").grid(row=0,
                                                                                                            column=2,
                                                                                                            padx=5,
                                                                                                            pady=5)

        # Chart Area
        self.chart_frame = ttk.Frame(self.master)
        self.chart_frame.pack(fill="both", expand=True, pady=10, padx=10)

    def load_logo(self, frame):
        try:
            image = Image.open("QuantSPY.png")
            image = image.resize((200, 200), Image.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            logo_label = ttk.Label(frame, image=photo)
            logo_label.image = photo
            logo_label.pack()
        except Exception as e:
            print(f"Error loading logo: {e}")

    def analyze_stock(self):
        symbol = self.symbol_entry.get().upper()

        if not symbol:
            Messagebox.show_error("Error", "Please enter a stock symbol")
            return

        try:
            if self.api_var.get() == "Alpha Vantage":
                if not self.api_key.get():
                    Messagebox.show_error("Error", "Please enter your Alpha Vantage API key")
                    return
                self.data = self.get_stock_data_alpha_vantage(symbol)
                self.spy_data = self.get_stock_data_alpha_vantage('SPY')
            else:
                self.data = self.get_stock_data_yahoo(symbol)
                self.spy_data = self.get_stock_data_yahoo('SPY')

            # Calculate Relative Strength
            relative_strength = calculate_relative_strength(self.data, self.spy_data)
            print(f"Relative Strength: {relative_strength}")

            # Format relative_strength as a string
            if relative_strength is None or np.isnan(relative_strength):
                relative_strength = "N/A"
            else:
                relative_strength = f"{relative_strength:.4f}"

            self.plot_stock_chart(self.data, symbol, relative_strength)
        except Exception as e:
            print(f"Error in analyze_stock: {str(e)}")
            traceback.print_exc()
            Messagebox.show_error("Error", str(e))

    def get_stock_data_alpha_vantage(self, symbol):
        ts = TimeSeries(key=self.api_key.get(), output_format='pandas')
        data, _ = ts.get_intraday(symbol=symbol, interval='5min', outputsize='full')
        df = data.iloc[::-1]
        df.columns = ['open', 'high', 'low', 'close', 'volume']
        return df

    def get_stock_data_yahoo(self, symbol):
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="1d", interval="5m")
        df.columns = df.columns.str.lower()
        return df

    def plot_stock_chart(self, df, symbol, relative_strength):
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        fig, ax = plt.subplots(figsize=(10, 6))

        # Check if relative_strength is already a string
        if isinstance(relative_strength, str):
            relative_strength_text = f"Relative Strength: {relative_strength}"
        else:
            # If it's not a string, assume it's a float and format it
            relative_strength_text = f"Relative Strength: {relative_strength:.4f}"

        plot_stock_data(fig, df, symbol, relative_strength=relative_strength_text)

        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def apply_hmm_analysis(self):
        if self.data is None:
            ttk.Messagebox.show_error("Error", "Please analyze a stock first")
            return

        try:
            print("Apply HMM button clicked")
            returns = self.data['close'].pct_change().dropna().values

            # Initialize and train HMM
            self.hmm = stock_hmm.StockHMM(self.num_states.get())
            self.hmm.baum_welch(returns.tolist(), 100, 1e-6)

            # Predict next return
            predicted_return = self.hmm.predict_next_return()

            # Get trading signals for the entire history
            trading_signals = self.hmm.get_trading_signals(returns.tolist())

            # Show HMM visualization in a separate window
            self.master.after(100, lambda: self.show_hmm_visualization(returns, predicted_return, trading_signals))

        except Exception as e:
            print(f"Error in apply_hmm_analysis: {str(e)}")
            traceback.print_exc()
            ttk.Messagebox.show_error("Error", f"An error occurred: {str(e)}")

    def show_hmm_visualization(self, returns, predicted_return, trading_signals):
        hmm_window = ttk.Toplevel(self.master)
        hmm_window.title(f"HMM Analysis for {self.symbol_entry.get().upper()}")
        hmm_window.geometry("1200x800")

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True, gridspec_kw={'height_ratios': [3, 1]})
        fig.patch.set_facecolor('black')

        dates = self.data.index[-len(returns):]
        prices = self.data['close'].iloc[-len(returns):]

        # Plot stock prices as a line chart
        ax1.plot(dates, prices, label='Close Price', color='white', linewidth=1)

        # Color the price line based on trading signals
        signal_colors = {'BUY': 'green', 'SELL': 'red', 'HOLD': 'gray'}
        for i, (date, price, signal) in enumerate(zip(dates, prices, trading_signals)):
            if i > 0:
                ax1.plot(dates[i - 1:i + 1], prices[i - 1:i + 1], color=signal_colors[signal], linewidth=2)

        ax1.set_title(f"Stock Price and HMM Analysis for {self.symbol_entry.get().upper()}", color='white')
        ax1.set_ylabel("Price ($)", color='white')
        ax1.tick_params(axis='y', colors='white')
        ax1.legend(loc='upper left')

        # Add price information
        current_price = prices.iloc[-1]
        day_high = prices.max()
        day_low = prices.min()
        price_info = f"Current: ${current_price:.2f}\nHigh: ${day_high:.2f}\nLow: ${day_low:.2f}"
        ax1.text(0.02, 0.05, price_info, transform=ax1.transAxes, fontsize=10,
                 verticalalignment='bottom', color='white', bbox=dict(facecolor='black', alpha=0.7))

        # Plot returns as a line
        ax2.plot(dates, returns, color='blue', linewidth=1)
        ax2.fill_between(dates, returns, 0, where=(returns > 0), facecolor='green', alpha=0.3)
        ax2.fill_between(dates, returns, 0, where=(returns <= 0), facecolor='red', alpha=0.3)
        ax2.axhline(y=0, color='white', linestyle='-', linewidth=0.5)
        ax2.set_ylabel("Returns (%)", color='white')
        ax2.set_xlabel("Date", color='white')
        ax2.tick_params(axis='y', colors='white')

        # Add returns information
        mean_return = np.mean(returns) * 100
        std_return = np.std(returns) * 100
        returns_info = f"Mean: {mean_return:.2f}%\nStd Dev: {std_return:.2f}%"
        ax2.text(0.02, 0.95, returns_info, transform=ax2.transAxes, fontsize=10,
                 verticalalignment='top', color='white', bbox=dict(facecolor='black', alpha=0.7))

        # Plot predicted return
        if not np.isnan(predicted_return):
            predicted_price = current_price * (1 + predicted_return)
            ax1.axhline(y=predicted_price, color='yellow', linestyle='--',
                        label=f'Predicted Next Close: ${predicted_price:.2f}')
            ax1.text(dates[-1], predicted_price, f'${predicted_price:.2f}', color='yellow', ha='right', va='bottom')

        # Add current trading signal
        current_signal = trading_signals[-1] if trading_signals else "N/A"
        ax1.text(0.02, 0.95, f"Current Signal: {current_signal}", transform=ax1.transAxes, fontsize=12,
                 verticalalignment='top', color='white', bbox=dict(facecolor='black', alpha=0.7))

        # Create a custom legend for trading signals
        from matplotlib.lines import Line2D
        legend_elements = [Line2D([0], [0], color=c, lw=2, label=s) for s, c in signal_colors.items()]
        ax1.legend(handles=legend_elements, loc='upper left', title='Signals')

        date_formatter = mdates.DateFormatter('%Y-%m-%d %I:%M %p')  # %I for 12-hour clock, %p for AM/PM
        ax1.xaxis.set_major_formatter(date_formatter)
        ax2.xaxis.set_major_formatter(date_formatter)

        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=hmm_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        toolbar = NavigationToolbar2Tk(canvas, hmm_window)
        toolbar.update()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        close_button = ttk.Button(hmm_window, text="Close", command=hmm_window.destroy, style="danger.TButton")
        close_button.pack(pady=10)

    def visualize_results(self):
        try:
            for widget in self.chart_frame.winfo_children():
                widget.destroy()

            fig, ax = plt.subplots(figsize=(10, 6))

            if not isinstance(self.data, pd.DataFrame):
                raise TypeError("self.data must be a pandas DataFrame")

            close_data = self.data['close']
            volume_data = self.data['volume']

            ax.plot(self.data.index, close_data, label='Close Price')

            dc_result = directional_change(self.data['high'], self.data['low'], self.data['close'])
            for event in dc_result['events']:
                ax.axvline(x=self.data.index[event['index']], color='g' if event['type'] == 'bullish' else 'r',
                           linestyle='--', alpha=0.5)

            trendlines = calculate_trendlines(self.data)
            for trendline in trendlines:
                if isinstance(trendline, dict):
                    start = int(trendline['start'])
                    end = int(trendline['end'])
                    x = self.data.index[start:end]
                    y = trendline['line']
                    color = 'g' if trendline.get('type') == 'support' else 'r'
                    ax.plot(x, y, color=color, linewidth=2, label=trendline.get('type', 'Trendline'))
                else:
                    print(f"Unexpected trendline format: {trendline}")

            ax.set_title(f"Stock Analysis for {self.symbol_entry.get().upper()}")
            ax.set_xlabel("Time")
            ax.set_ylabel("Price")
            ax.legend()

            ax2 = ax.twinx()
            ax2.bar(self.data.index, volume_data, alpha=0.3, color='gray')
            ax2.set_ylabel('Volume')

            if len(self.data) > 5:
                tick_locations = self.data.index[::len(self.data) // 5]
                ax.set_xticks(tick_locations)
                ax.set_xticklabels([str(t) for t in tick_locations], rotation=45)

            # Calculate and display Relative Strength
            relative_strength = calculate_relative_strength(self.data, self.spy_data)
            ax.text(0.02, 0.98, f"Relative Strength: {relative_strength:.4f}", transform=ax.transAxes,
                    verticalalignment='top', fontsize=10, bbox=dict(facecolor='white', alpha=0.7))

            canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)

        except Exception as e:
            print(f"Error in visualize_results: {str(e)}")
            print(f"Type of self.data: {type(self.data)}")
            if isinstance(self.data, pd.DataFrame):
                print(f"Columns of self.data: {self.data.columns}")
            traceback.print_exc()
            ttk.Messagebox.show_error("Error", f"An error occurred while visualizing: {str(e)}")


if __name__ == "__main__":
    try:
        root = ttk.Window(themename="darkly")
        app = StockAnalyzerGUI(root)
        root.mainloop()
    except Exception as e:
        print("An error occurred:")
        traceback.print_exc()