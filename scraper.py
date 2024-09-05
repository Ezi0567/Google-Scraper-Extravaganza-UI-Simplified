import json
import os
import csv
import random
import time
import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup

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

def save_results(results, query, domain):
    """Saves the scraped results to a CSV file."""
    filename = os.path.join("results", f"{datetime.now().strftime('%Y-%m-%d')}_{domain}_{query}.csv")
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['page', 'position', 'title', 'url']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    # Debugging output
    print(f"Saved results to {filename}")

def scrape_and_save(query, num_pages, domain, gl):
    """Scrapes and saves results for a specific domain and geolocation."""
    results = scrape_results(query, num_pages, domain, gl)
    if results:  # Only save if results were fetched
        save_results(results, query, domain)
    else:
        print(f"No results found for {domain} with geolocation {gl}")

if __name__ == "__main__":
    query = config['query']
    num_pages = config['num_pages']

    # Prepare tasks for concurrent execution
    tasks = [(query, num_pages, domain, gl) for domain in DOMAINS for gl in GEOLOCATIONS]

    # Use ThreadPoolExecutor to handle concurrency
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(scrape_and_save, *task) for task in tasks]

        for future in as_completed(futures):
            try:
                future.result()  # Check for exceptions
            except Exception as e:
                print(f"Task error: {e}")
