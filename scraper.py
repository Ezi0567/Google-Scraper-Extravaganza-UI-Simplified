import json
import os
import random
import time
import requests
import tkinter as tk
import pandas as pd
from tkinter import messagebox
import subprocess
import sys
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup

# Function to install packages using pip
def install_packages():
    required_packages = ["requests", "beautifulsoup4", "pandas", "openpyxl"]  # Add the packages you need here
    
    try:
        for package in required_packages:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        messagebox.showinfo("Success", "Packages installed successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to install packages: {e}")

def save_data():
    geolocations = geoloc_var.get()
    domains = domain_var.get()
    search_query = search_query_entry.get()
    num_pages = num_pages_entry.get()

    # Prepare data dictionary
    data = {
        "geolocations": geolocations.split(","),  # Splitting comma-separated values into a list
        "domains": domains.split(","),
        "search_query": search_query,
        "num_pages": num_pages
    }

    # Path to save the JSON file
    json_file_path = "search_data.json"

    # Write to the JSON file
    try:
        with open(json_file_path, 'w') as file:
            json.dump(data, file, indent=4)
        messagebox.showinfo("Success", "Data saved successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save data: {e}")

def start_scraping():
    query = search_query_entry.get()
    geolocations = geoloc_var.get().split(',')
    domains = domain_var.get().split(',')
    num_pages = int(num_pages_entry.get())  # Get the number of pages from the user input

    # Prepare tasks for concurrent execution
    tasks = [(query, num_pages, domain, gl) for domain in domains for gl in geolocations]

    # Use ThreadPoolExecutor to handle concurrency
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(scrape_and_save, *task) for task in tasks]

        for future in as_completed(futures):
            try:
                future.result()  # Check for exceptions
            except Exception as e:
                print(f"Task error: {e}")

    messagebox.showinfo("Scraping Complete", "Data scraping has been completed!")

# Load configuration
with open('config.json') as f:
    config = json.load(f)

with open('user_agents.json') as f:
    user_agents = json.load(f)['user_agents']

# Hardcoded domains and geolocations
DOMAINS = config['domains']
GEOLOCATIONS = config['geolocations']

def get_random_user_agent():
    """Returns a random user agent from the list.""" 
    return random.choice(user_agents)

def scrape_results(query, num_pages, domain, gl):
    """Scrapes search results from Google for a specific domain and geolocation.""" 
    results = []
    base_url = f"https://{domain}/search"

    for page in range(num_pages):
        headers = {'User-Agent': get_random_user_agent()}
        params = {
            'q': query,
            'start': page * 10,
            'gl': gl  # Geolocation parameter
        }

        try:
            response = requests.get(base_url, headers=headers, params=params)
            response.raise_for_status()  # Raise exception for HTTP errors

            html = response.text
            page_results = parse_results(html, page)
            results.extend(page_results)

            # Debugging output
            print(f"Scraped page {page + 1} from {domain} with geolocation {gl}")

        except requests.RequestException as e:
            print(f"Request error: {e}")
            time.sleep(5)  # Longer delay after error
            continue

        time.sleep(random.uniform(1, 3))  # Random delay between requests

    return results

def parse_results(html, page):
    """Parses HTML to extract search results.""" 
    soup = BeautifulSoup(html, 'lxml')  # Use lxml parser
    results = []
    result_divs = soup.find_all('div', class_='g')  # Google search result container

    for position, result_div in enumerate(result_divs, start=1):
        title_elem = result_div.find('h3')
        url_elem = result_div.find('a')

        if title_elem and url_elem:
            title = title_elem.get_text()
            url = url_elem.get('href')
            results.append({
                'page': page + 1,  # Pages are 1-indexed
                'position': position,
                'title': title,
                'url': url
            })

    return results

def save_results_as_excel(results, query, domain):
    """Saves the scraped results to an Excel file.""" 
    filename = os.path.join("results", f"{datetime.now().strftime('%Y-%m-%d')}_{domain}_{query}.xlsx")
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    df = pd.DataFrame(results)
    df.to_excel(filename, index=False)

    print(f"Saved results to {filename}")

def scrape_and_save(query, num_pages, domain, gl):
    """Scrapes and saves results for a specific domain and geolocation.""" 
    results = scrape_results(query, num_pages, domain, gl)
    if results:  # Only save if results were fetched
        save_results_as_excel(results, query, domain)
    else:
        print(f"No results found for {domain} with geolocation {gl}")

# Tkinter UI setup
root = tk.Tk()
root.title("Google Scraper Config")

# Labels and input fields
tk.Label(root, text="Search Query:").grid(row=0, column=0, padx=10, pady=5)
search_query_entry = tk.Entry(root, width=40)
search_query_entry.grid(row=0, column=1, padx=10, pady=5)

tk.Label(root, text="Domains:").grid(row=1, column=0, padx=10, pady=5)
domain_var = tk.StringVar(root)
domain_var.set(DOMAINS[0])  # Set the default value
domain_menu = tk.OptionMenu(root, domain_var, *DOMAINS)
domain_menu.grid(row=1, column=1, padx=10, pady=5)

tk.Label(root, text="Geolocations:").grid(row=2, column=0, padx=10, pady=5)
geoloc_var = tk.StringVar(root)
geoloc_var.set(GEOLOCATIONS[0])  # Set the default value
geoloc_menu = tk.OptionMenu(root, geoloc_var, *GEOLOCATIONS)
geoloc_menu.grid(row=2, column=1, padx=10, pady=5)

tk.Label(root, text="Number of Pages:").grid(row=3, column=0, padx=10, pady=5)
num_pages_entry = tk.Entry(root, width=10)
num_pages_entry.grid(row=3, column=1, padx=10, pady=5)

# Save Data Button
save_button = tk.Button(root, text="Save Data", command=save_data)
save_button.grid(row=4, column=0, columnspan=2, pady=10)

# Install Packages Button
install_button = tk.Button(root, text="Install Required Packages", command=install_packages)
install_button.grid(row=5, column=0, columnspan=2, pady=10)

# Scrape Data Button
scrape_button = tk.Button(root, text="Scrape Data", command=start_scraping)
scrape_button.grid(row=6, column=0, columnspan=2, pady=10)

# Run the Tkinter event loop
root.mainloop()
