import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from data_fetcher import fetch_spy_data_for_today
from vwap_calculation import calculate_vwap_with_bands_and_signals
from plotter import plot_data_with_signals  # Import the plot function

class FinancialAnalysisApp:
    def __init__(self, root):
        self.root = root
        self.root.title("QuantiSPY")

        #window dimension
        self.root.geometry("500x500")
        self.add_logo()

    def add_logo(self):
        self.logo = tk.PhotoImage(file="spy_data/QuantiSPY.png")
        self.logo_label = tk.Label(self.root, image=self.logo)
        self.logo_label.pack(pady=10)  # Adjust padding as needed

        # Initialize data file variable
        self.data_csv = None

        # Create UI components
        self.create_widgets()

    def create_widgets(self):
        # Fetch Historical Data Button
        self.fetch_data_button = tk.Button(self.root, text="Fetch Historical Data", command=self.fetch_historical_data)
        self.fetch_data_button.pack(pady=10)

        # Load Data Button
        self.load_button = tk.Button(self.root, text="Load Data", command=self.load_data)
        self.load_button.pack(pady=10)

        # Calculate VWAP Button
        self.calculate_vwap_button = tk.Button(self.root, text="Calculate VWAP", command=self.calculate_vwap)
        self.calculate_vwap_button.pack(pady=10)

        # Plot Data Button
        self.plot_data_with_signals_button = tk.Button(self.root, text="Plot Data", command=self.plot_data)
        self.plot_data_with_signals_button.pack(pady=10)

        # Status Label - ensure this is created properly
        self.status_label = tk.Label(self.root, text="Status: Ready")
        self.status_label.pack(pady=10)

    def fetch_historical_data(self):
        """Fetch historical data and save to a CSV file."""
        try:
            start_date = simpledialog.askstring("Input", "Enter start date (YYYY-MM-DD):")
            end_date = simpledialog.askstring("Input", "Enter end date (YYYY-MM-DD):")

            if not start_date or not end_date:
                raise ValueError("Start date and end date must be provided.")

            output_csv = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])

            if not output_csv:
                raise ValueError("Output file path must be provided.")

            fetch_spy_data_for_today(output_csv)
            self.status_label.config(text=f"Historical data fetched and saved to {output_csv}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch historical data: {e}")
            self.status_label.config(text="Failed to fetch historical data.")

    def load_data(self):
        """Open file dialog to load CSV data."""
        self.data_csv = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if self.data_csv:
            self.status_label.config(text=f"Loaded file: {self.data_csv}")
        else:
            self.status_label.config(text="No file selected.")

    def calculate_vwap(self):
        """Calculate VWAP from the loaded CSV file."""
        if not self.data_csv:
            messagebox.showerror("Error", "No data file loaded. Please load a CSV file first.")
            return

        try:
            vwap_period = simpledialog.askinteger("Input", "Enter VWAP period (number of bars):")

            if not vwap_period:
                raise ValueError("VWAP period must be provided.")

            calculate_vwap_with_bands_and_signals(self.data_csv, vwap_period, band_multiplier=1)
            self.status_label.config(text=f"VWAP calculation complete. Output saved.")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to calculate VWAP: {e}")
            self.status_label.config(text="Failed to calculate VWAP.")

    def plot_data(self):
        """Plot the loaded CSV data with signals."""
        if not self.data_csv:
            messagebox.showerror("Error", "No data file loaded. Please load a CSV file first.")
            return

        try:
            # Call the plot function from plotter
            plot_data_with_signals(self.data_csv)
            self.status_label.config(text="Data plotted successfully.")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to plot data: {e}")
            self.status_label.config(text="Failed to plot data.")


# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = FinancialAnalysisApp(root)
    root.mainloop()
