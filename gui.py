import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from alpha_vantage.timeseries import TimeSeries
import pandas as pd
import yfinance as yf
from plotter import plot_stock_data
from PIL import Image, ImageTk

class StockAnalyzerGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("QuantiSPY: Instant Technical Analysis")
        self.master.geometry("800x700")  # Increased height to accommodate logo

        self.api_var = tk.StringVar(value="Alpha Vantage")
        self.api_key = tk.StringVar()

        self.create_widgets()

    def create_widgets(self):
        # Logo
        logo_frame = ttk.Frame(self.master)
        logo_frame.pack(pady=10)
        self.load_logo(logo_frame)

        # API Selection
        api_frame = ttk.Frame(self.master)
        api_frame.pack(pady=10)
        ttk.Label(api_frame, text="Select API:").pack(side=tk.LEFT)
        ttk.Radiobutton(api_frame, text="Alpha Vantage", variable=self.api_var, value="Alpha Vantage").pack(
            side=tk.LEFT)
        ttk.Radiobutton(api_frame, text="Yahoo Finance", variable=self.api_var, value="Yahoo Finance").pack(
            side=tk.LEFT)

        # API Key Input (for Alpha Vantage)
        key_frame = ttk.Frame(self.master)
        key_frame.pack(pady=10)
        ttk.Label(key_frame, text="Alpha Vantage API Key:").pack(side=tk.LEFT)
        ttk.Entry(key_frame, textvariable=self.api_key, width=40).pack(side=tk.LEFT)

        # Stock Symbol Input
        input_frame = ttk.Frame(self.master)
        input_frame.pack(pady=10)
        ttk.Label(input_frame, text="Enter Stock Symbol:").pack(side=tk.LEFT)
        self.symbol_entry = ttk.Entry(input_frame, width=10)
        self.symbol_entry.pack(side=tk.LEFT)
        ttk.Button(input_frame, text="Analyze", command=self.analyze_stock).pack(side=tk.LEFT)

        # Chart Area
        self.chart_frame = ttk.Frame(self.master)
        self.chart_frame.pack(fill=tk.BOTH, expand=True)

    def load_logo(self, frame):
        try:
            # Load and resize the image
            image = Image.open("QuantSPY.png")
            image = image.resize((200, 200), Image.LANCZOS)  # Adjust size as needed
            photo = ImageTk.PhotoImage(image)

            # Create a label and display the image
            logo_label = ttk.Label(frame, image=photo)
            logo_label.image = photo  # Keep a reference
            logo_label.pack()
        except Exception as e:
            print(f"Error loading logo: {e}")

    def analyze_stock(self):
        symbol = self.symbol_entry.get().upper()
        if not symbol:
            messagebox.showerror("Error", "Please enter a stock symbol")
            return

        try:
            if self.api_var.get() == "Alpha Vantage":
                if not self.api_key.get():
                    messagebox.showerror("Error", "Please enter your Alpha Vantage API key")
                    return
                df = self.get_stock_data_alpha_vantage(symbol)
            else:
                df = self.get_stock_data_yahoo(symbol)

            self.plot_stock_chart(df, symbol)
        except Exception as e:
            messagebox.showerror("Error", str(e))

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

    def plot_stock_chart(self, df, symbol):
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        fig, ax = plt.subplots(figsize=(10, 6))
        plot_stock_data(fig, df, symbol)

        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = StockAnalyzerGUI(root)
    root.mainloop()