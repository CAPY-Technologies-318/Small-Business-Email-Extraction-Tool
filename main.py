import subprocess
import sys

def launch_gui():
    print("Launching GUI...")
    subprocess.run([sys.executable, "gui.py"])

def run_google_maps_scraper():
    search = input("Enter search keyword (e.g. 'dentist'): ").strip()
    zips = input("Enter ZIP codes (space-separated, leave blank for auto): ").strip().split()
    command = [sys.executable, "google-map.py", "-s", search]
    if zips:
        command += ["--zipcodes"] + zips
    subprocess.run(command)

def run_email_crawler():
    domain = input("Enter website domain (e.g. shopcommunal.com): ").strip()
    full_url = "https://" + domain if not domain.startswith("http") else domain
    subprocess.run([sys.executable, "crawler.py", full_url])

def main():
    print("\n== CAPY Technologies Scraper Launcher ==")
    print("1. Run GUI")
    print("2. Run Google Maps Scraper (CLI)")
    print("3. Run Email Crawler (CLI)")
    print("0. Exit")

    choice = input("Select an option: ").strip()

    if choice == "1":
        launch_gui()
    elif choice == "2":
        run_google_maps_scraper()
    elif choice == "3":
        run_email_crawler()
    elif choice == "0":
        print("Goodbye!")
        sys.exit()
    else:
        print("Invalid choice.")
        main()

if __name__ == "__main__":
    main()
