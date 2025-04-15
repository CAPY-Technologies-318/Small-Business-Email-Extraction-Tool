import tkinter as tk
from tkinter import messagebox, filedialog
import subprocess
import pandas as pd
import threading
import glob
import os

def run_command_live(command, output_box, on_complete=None):
    def _run():
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        for line in process.stdout:
            output_box.insert(tk.END, line)
            output_box.see(tk.END)
            output_box.update_idletasks()
        process.wait()
        if on_complete:
            on_complete()

    threading.Thread(target=_run).start()

def run_search():
    """
    Main function to execute the search process.
    - Validates the search query input
    - Runs the google_search_scraper.py with appropriate parameters
    - Displays results or errors in the output text area
    """
    query = entry.get().strip()
    if not query:
        messagebox.showwarning("Input Error", "Please enter a search query.")
        return
    
    try:
        # Get the number of results from the entry field
        num_results = num_results_entry.get().strip()
        if not num_results:
            num_results = "10"  # Default value
        
        # Build the command
        command = ['python', 'google_search_scraper.py', query, f'--num_results={num_results}']
        
        # Add headless mode if checkbox is checked
        if headless_var.get():
            command.append('headless=true')
        else:
            command.append('headless=false')
        
        output_text.delete("1.0", tk.END)
        output_text.insert(tk.END, f"[INFO] Starting search for: {query}\n")
        output_text.insert(tk.END, f"[INFO] Number of results: {num_results}\n\n")
        
        run_command_live(command, output_text)
    except Exception as e:
        messagebox.showerror("Execution Error", str(e))

def export_as_csv():
    """
    Exports the search results to a CSV file.
    """
    try:
        # Check if there are any results in the output directory
        csv_files = glob.glob("output/*.csv")
        if not csv_files:
            messagebox.showwarning("No Data", "No search results found to export.")
            return

        # Get the most recent CSV file
        latest_file = max(csv_files, key=os.path.getctime)
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile="search_results.csv"
        )
        
        if file_path:
            # Copy the file to the selected location
            import shutil
            shutil.copy2(latest_file, file_path)
            messagebox.showinfo("Export", f"Search results exported to:\n{file_path}")
    except Exception as e:
        messagebox.showerror("Export Error", str(e))

def export_as_excel():
    """
    Exports the search results to an Excel file.
    """
    try:
        csv_files = glob.glob("output/*.csv")
        if not csv_files:
            messagebox.showwarning("No Data", "No search results found to export.")
            return

        # Get the most recent CSV file
        latest_file = max(csv_files, key=os.path.getctime)
        
        # Read the CSV file
        df = pd.read_csv(latest_file)
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            initialfile="search_results.xlsx"
        )
        
        if file_path:
            df.to_excel(file_path, index=False)
            messagebox.showinfo("Export", f"Search results exported to:\n{file_path}")
    except Exception as e:
        messagebox.showerror("Export Error", str(e))

def export_as_txt():
    """
    Exports the search results to a text file.
    """
    try:
        csv_files = glob.glob("output/*.csv")
        if not csv_files:
            messagebox.showwarning("No Data", "No search results found to export.")
            return

        # Get the most recent CSV file
        latest_file = max(csv_files, key=os.path.getctime)
        
        # Read the CSV file
        df = pd.read_csv(latest_file)
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")],
            initialfile="search_results.txt"
        )
        
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                for _, row in df.iterrows():
                    f.write(f"URL: {row.get('url', 'N/A')}\n")
                    f.write(f"Emails: {', '.join(row.get('emails', []))}\n")
                    f.write("-" * 50 + "\n")
            messagebox.showinfo("Export", f"Search results exported to:\n{file_path}")
    except Exception as e:
        messagebox.showerror("Export Error", str(e))

# GUI Setup
root = tk.Tk()
root.title("Google Search Scraper")

# Search Query Input Section
tk.Label(root, text="Search Query:").pack(pady=(10, 0))
entry = tk.Entry(root, width=40)
entry.pack(pady=5)

# Number of Results Input Section
tk.Label(root, text="Number of Results:").pack(pady=(5, 0))
num_results_entry = tk.Entry(root, width=40)
num_results_entry.pack(pady=(0, 5))
num_results_entry.insert(0, "10")  # Default value

# Headless Mode Checkbox
headless_var = tk.BooleanVar(value=True)
headless_checkbox = tk.Checkbutton(root, text="Run in headless mode", variable=headless_var)
headless_checkbox.pack(pady=5)

# Button Frame for Action Buttons
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

# Start Search Button
start_button = tk.Button(button_frame, text="Start Search", command=run_search)
start_button.pack(side=tk.LEFT, padx=5)

# Export Dropdown Menu
export_button = tk.Menubutton(button_frame, text="Export", relief=tk.RAISED)
export_menu = tk.Menu(export_button, tearoff=0)
export_menu.add_command(label=".csv", command=export_as_csv)
export_menu.add_command(label=".xlsx", command=export_as_excel)
export_menu.add_command(label=".txt", command=export_as_txt)
export_button["menu"] = export_menu
export_button.pack(side=tk.LEFT, padx=5)

# Output Text Area
output_text = tk.Text(root, height=20, width=80)
output_text.pack(pady=(0, 10))

# Start the GUI Event Loop
root.mainloop() 