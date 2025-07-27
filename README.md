# Small Business Email Extraction Tool

A comprehensive Python toolkit for extracting business information and email addresses from Google Maps, Google Search, and business websites. This tool provides both command-line functionality and user-friendly GUI interfaces for business data collection and email harvesting.

## 🌟 Features

### Core Functionality
- **Google Maps Business Scraping**: Extract business information (name, address, phone, website) from Google Maps searches
- **Google Search Scraping**: Perform automated Google searches and collect business data
- **Email Extraction**: Extract email addresses from business websites using multiple methods
- **ZIP Code Integration**: Search businesses within specific ZIP codes using included US ZIP code database
- **Multiple Output Formats**: Export data to CSV and Excel formats

### User Interfaces
- **Main GUI**: Comprehensive interface for Google Maps scraping and email extraction
- **Search GUI**: Specialized interface for Google Search operations
- **Real-time Output**: Live command output display during scraping operations

### Technical Features
- **Multiple Scraping Methods**: Uses both Selenium and Playwright for robust web scraping
- **Anti-Detection**: Built-in measures to avoid bot detection
- **Progress Tracking**: Real-time progress bars and status updates
- **Error Handling**: Comprehensive error handling and logging
- **Headless Operation**: Option to run browsers in headless mode for faster processing

## 🚀 Quick Start

### Prerequisites
- Python 3.7 or higher
- macOS, Windows, or Linux

### Installation

#### Option 1: One-Click Setup (macOS/Linux)
```bash
# Make the run script executable
chmod +x run.command

# Run the setup and launch script
./run.command
```

#### Option 2: Manual Setup
```bash
# Clone the repository
git clone https://github.com/CAPY-Technologies-318/Small-Business-Email-Extraction-Tool.git
cd Small-Business-Email-Extraction-Tool

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
python -m playwright install

# Launch main GUI
python gui.py
```

### Quick Launch Scripts
- **Main GUI**: `python gui.py`
- **Search GUI**: `python search_scraper_gui.py` or `./search_scraper.command`

## 📖 Usage Guide

### 1. Google Maps Business Scraping

Use the main GUI (`gui.py`) to scrape business data from Google Maps:

1. **Launch the application**:
   ```bash
   python gui.py
   ```

2. **Enter search parameters**:
   - Business type (e.g., "restaurants", "dentists", "law firms")
   - ZIP code(s) for geographic targeting
   - Number of results to collect

3. **Start scraping**: The tool will automatically:
   - Search Google Maps for businesses
   - Extract business information (name, address, phone, website)
   - Save results to CSV format in the `output/` directory

### 2. Google Search Scraping

Use the search GUI (`search_scraper_gui.py`) for Google Search operations:

1. **Launch the search interface**:
   ```bash
   python search_scraper_gui.py
   ```

2. **Configure search parameters**:
   - Search query
   - Number of results
   - Headless mode option

3. **Export options**: Results can be exported to CSV or Excel formats

### 3. Email Extraction

Extract emails from business websites using multiple methods:

#### Method 1: Simple Extraction
```python
from website_email_scraper import scrape_website_emails

emails = scrape_website_emails("https://example-business.com")
print(emails)
```

#### Method 2: Advanced Extraction (with Selenium)
```python
from crawler import scrape_website_emails

emails = scrape_website_emails("https://example-business.com")
print(emails)
```

### 4. Automated Workflow

For a complete business data + email extraction workflow:

1. Use Google Maps scraping to collect business websites
2. Use the email extraction feature to crawl collected websites
3. Export combined data with business info and email addresses

## 📁 Project Structure

```
Small-Business-Email-Extraction-Tool/
├── gui.py                      # Main GUI interface
├── search_scraper_gui.py       # Search-focused GUI
├── google-map.py              # Google Maps scraping engine
├── google_search_scraper.py   # Google Search scraping engine
├── crawler.py                 # Advanced email scraper (Selenium)
├── website_email_scraper.py   # Simple email scraper (requests)
├── requirements.txt           # Python dependencies
├── us_zipcodes.csv           # US ZIP code database (33k+ entries)
├── run.command               # macOS/Linux setup script
├── search_scraper.command    # macOS/Linux search launcher
└── output/                   # Generated data files
```

## 🛠️ Configuration

### Environment Setup
The tool automatically detects your system and configures appropriate browser drivers. For manual configuration:

```python
# Headless mode (faster, no browser window)
headless = True

# Custom delays (to avoid rate limiting)
delay_between_requests = 2  # seconds

# Custom output directory
output_dir = "my_custom_output/"
```

### ZIP Code Filtering
Use the included `us_zipcodes.csv` file to target specific geographic areas:

```python
# Filter by specific ZIP codes
target_zips = ["90210", "10001", "60601"]

# Filter by state
target_state = "CA"  # California only
```

## 📊 Output Formats

### CSV Output Structure
```csv
name,address,website,phone_number,emails
"ABC Restaurant","123 Main St, City, State","https://abc-restaurant.com","(555) 123-4567","info@abc-restaurant.com,orders@abc-restaurant.com"
```

### Excel Output
- Multiple worksheets for different data types
- Formatted columns with proper data types
- Automatic filtering and sorting options

## ⚠️ Important Considerations

### Legal and Ethical Use
- **Respect robots.txt**: Always check and respect website robots.txt files
- **Rate Limiting**: Built-in delays prevent overwhelming target servers
- **Terms of Service**: Ensure compliance with Google's Terms of Service
- **Data Privacy**: Handle collected data responsibly and in compliance with privacy laws

### Best Practices
- **Start Small**: Begin with small test runs to understand the tool
- **Regular Breaks**: Use delays between requests to avoid IP blocking
- **Data Validation**: Always verify and clean extracted data
- **Backup Results**: Regularly backup your output files

### Limitations
- **Rate Limits**: Google may impose rate limits on search requests
- **Dynamic Content**: Some websites may not load content without JavaScript
- **Geographic Restrictions**: Some results may vary by geographic location

## 🔧 Dependencies

### Core Dependencies
- **playwright**: Modern web automation
- **selenium**: Web browser automation
- **beautifulsoup4**: HTML parsing
- **pandas**: Data manipulation and analysis
- **requests**: HTTP library
- **tqdm**: Progress bars

### GUI Dependencies
- **tkinter**: GUI framework (included with Python)
- **openpyxl**: Excel file handling

### Optional Dependencies
- **flask**: Web interface (if using web-based GUI)

## 🐛 Troubleshooting

### Common Issues

#### Browser Installation
```bash
# If Playwright browsers fail to install
python -m playwright install chromium
python -m playwright install-deps
```

#### Permission Errors (macOS)
```bash
# Make scripts executable
chmod +x run.command
chmod +x search_scraper.command
```

#### Module Not Found Errors
```bash
# Ensure virtual environment is activated
source venv/bin/activate
pip install -r requirements.txt
```

### Performance Issues
- **Memory Usage**: Large datasets may require more RAM
- **Speed Optimization**: Use headless mode for faster processing
- **Network Issues**: Check internet connection and firewall settings

## 📈 Advanced Usage

### Custom Search Patterns
```python
# Advanced Google Maps search patterns
search_patterns = [
    "restaurants near {zipcode}",
    "dentists in {zipcode}",
    "{business_type} {city} {state}"
]
```

### Batch Processing
```python
# Process multiple ZIP codes
zipcodes = ["90210", "10001", "60601"]
for zipcode in zipcodes:
    results = scrape_businesses_by_zipcode(zipcode)
    save_results(results, f"output/{zipcode}_results.csv")
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚡ Support

For support, issues, or feature requests:
- Open an issue on GitHub
- Check the troubleshooting section above
- Review the code comments for detailed functionality

## 🔄 Updates

This tool is actively maintained. Check for updates regularly:
```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

---

**Disclaimer**: This tool is for educational and legitimate business purposes only. Users are responsible for ensuring compliance with all applicable laws, terms of service, and ethical guidelines when collecting data from websites.