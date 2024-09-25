# 🚀 Google Scraper Extravaganza!

Welcome to the ultimate Google Scraper! This script is your ticket to scraping Google search results like a pro. Whether you're gathering data for research, a project, or just for the thrill of it, you've come to the right place!

## 🕵 What Does It Do?

My scraper takes your query and searches across Google’s .com and .co.uk domains. It’s designed to fetch results from various pages and save them in neatly organised CSV files. No proxies, no VPNs—just pure scraping goodness!

## Features 🎉

- Direct Search: Scrape results directly from Google’s .com and .co.uk domains.
- Multiple Pages: Fetch results from multiple pages of search results.
- Geolocation Targeting: Target results based on specific regions (e.g., US, UK).
- CSV Output: Results are saved in easily accessible CSV files.

## 🔧 How To Get Started

1. **Clone Or Download The Repository**


```bash
git clone https://github.com/recycledrobot/google-scraper.git
cd google-scraper
```

OR

https://github.com/recycledrobot/Google-Scraper-Extravaganza/archive/refs/heads/main.zip


2. **Install Dependencies**

Make sure you have Python installed, then run:

```bash
pip install -r requirements.txt
```

3. **Configure Your Scraper**

Update the `config.json` file to specify your search query, number of pages, and domains. Here’s a sample:

```json
{
  "query": "example search",
  "num_pages": 5,
  "domains": [
    "google.com",
    "google.co.uk"
  ],
  "geolocations": [
    "us",
    "uk"
  ]
}
```

4. **Run the Scraper**

Time to watch the magic happen! Run the scraper with:

```bash
python scraper.py
```

5. **Check The Results**

Results will be saved in the results folder, neatly organised by date, domain, and query.
