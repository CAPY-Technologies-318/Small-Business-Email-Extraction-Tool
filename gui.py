import tkinter as tk
from tkinter import messagebox, filedialog
import subprocess
import requests
import pandas as pd
import threading
import glob

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


def get_user_zip():
    """
    Attempts to get the user's ZIP code based on their IP address using ipinfo.io API.
    Returns an empty string if the request fails.
    """
    try:
        res = requests.get('http://ipinfo.io/json')
        data = res.json()
        return data.get('postal', '')
    except Exception as e:
        return ''

def crawl_emails_from_csv():
    try:
        df = pd.read_csv("output/google_maps_zipcode_data.csv")
        if "website" not in df.columns:
            messagebox.showerror("CSV Error", "No 'website' column found in the data.")
            return

        websites = df["website"].dropna().unique()

        output_text.delete("1.0", tk.END)
        output_text.insert(tk.END, "[INFO] Starting email crawl on collected websites...\n\n")

        for site in websites:
            if not isinstance(site, str) or not site.strip():
                continue
            # Show the site being processed
            output_text.insert(tk.END, f"\n[+] Crawling: {site}\n")
            output_text.see(tk.END)
            run_command_live(['python3', 'crawler.py', site], output_text)

    except Exception as e:
        messagebox.showerror("Email Crawling Error", str(e))


def run_script():
    """
    Main function to execute the scraping process.
    - Validates the search keyword input
    - Gets ZIP codes from user input or IP-based location
    - Runs the testingScript.py with appropriate parameters
    - Displays results or errors in the output text area
    """
    keyword = entry.get().strip()
    if not keyword:
        messagebox.showwarning("Input Error", "Please enter a search keyword.")
        return
    
    # Get the user's input for zip codes; if none, fall back to user's IP-based zip
    zip_codes_raw = zip_entry.get().strip()
    if not zip_codes_raw:
        zip_codes_raw = get_user_zip()

    # Split the zip codes string on spaces to allow multiple zip codes
    zip_codes_list = zip_codes_raw.split()

    try:
        # Pass each zip code as a separate argument after --zipcodes
        command = ['python3', 'google-map.py', '-s', keyword, '--zipcodes'] + zip_codes_list
        output_text.delete("1.0", tk.END)
        run_command_live(command, output_text, on_complete=crawl_emails_from_csv)
    except Exception as e:
        messagebox.showerror("Execution Error", str(e))

import glob
import os

def export_as_csv():
    """
    Merges all email CSV files in the output/ directory into one and exports it.
    """
    csv_files = glob.glob("output/*.csv")
    if not csv_files:
        messagebox.showwarning("No Data", "No CSV files found in the output directory.")
        return

    all_emails = []
    for file in csv_files:
        try:
            df = pd.read_csv(file)
            if "Email" in df.columns:
                df["source_file"] = os.path.basename(file)
                all_emails.append(df)
        except Exception as e:
            print(f"[WARN] Skipping {file}: {e}")

    if not all_emails:
        messagebox.showerror("Error", "No email data found to export.")
        return

    merged = pd.concat(all_emails, ignore_index=True)

    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if file_path:
        merged.to_csv(file_path, index=False)
        messagebox.showinfo("Export", f"Merged CSV exported to:\n{file_path}")

def export_as_excel():
    """
    Merges all email CSV files in the output/ directory into one Excel file.
    """
    csv_files = glob.glob("output/*.csv")
    all_emails = []

    for file in csv_files:
        try:
            df = pd.read_csv(file)
            if "Email" in df.columns:
                df["source_file"] = os.path.basename(file)
                all_emails.append(df)
        except Exception as e:
            print(f"[WARN] Skipping {file}: {e}")

    if not all_emails:
        messagebox.showerror("Export Error", "No email data found to export.")
        return

    merged = pd.concat(all_emails, ignore_index=True)

    file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
    if file_path:
        merged.to_excel(file_path, index=False)
        messagebox.showinfo("Export", f"Merged Excel file saved to:\n{file_path}")

def export_as_txt():
    """
    Merges all email CSV files and exports plain email addresses to a .txt file.
    """
    csv_files = glob.glob("output/*.csv")
    emails = set()

    for file in csv_files:
        try:
            df = pd.read_csv(file)
            if "Email" in df.columns:
                emails.update(df["Email"].dropna().unique())
        except Exception as e:
            print(f"[WARN] Skipping {file}: {e}")

    if not emails:
        messagebox.showerror("Export Error", "No email addresses found to export.")
        return

    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
    if file_path:
        with open(file_path, "w") as f:
            f.write("\n".join(sorted(emails)))
        messagebox.showinfo("Export", f"Email list saved to:\n{file_path}")

# GUI Setup
root = tk.Tk()
root.geometry("575x430")
root.resizable(False, False)
root.title("CAPY Business Data Scraper")

# Search Keyword Input Section
tk.Label(root, text="Search Business:").pack(pady=(10, 0))
entry = tk.Entry(root, width=40)
entry.pack(pady=5)

# ZIP Code Input Section
tk.Label(root, text="Zip Code:").pack(pady=(5, 0))
zip_entry = tk.Entry(root, width=40)
zip_entry.pack(pady=(0, 5))
zip_entry.insert(0, get_user_zip())  # Pre-fill with user's ZIP code

# Button Frame for Action Buttons
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

# Start Scraping Button
start_button = tk.Button(button_frame, text="Start", command=run_script)
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