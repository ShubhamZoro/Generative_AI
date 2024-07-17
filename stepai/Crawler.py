

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os

class WebCrawler:
    def __init__(self, start_url, keyword, max_depth, max_links):
        self.start_url = start_url
        self.keyword = keyword
        self.max_depth = max_depth
        self.max_links = max_links
        self.visited = set()
        self.to_visit = [(start_url, 0)]
        self.level_data = {}

    def crawl(self):
        while self.to_visit:
            url, depth = self.to_visit.pop(0)
            if depth > self.max_depth or url in self.visited:
                continue

            try:
                response = requests.get(url)
                response.raise_for_status()
            except requests.RequestException as e:
                print(f"Failed to retrieve {url}: {e}")
                continue

            self.visited.add(url)
            soup = BeautifulSoup(response.text, 'html.parser')

            if depth not in self.level_data:
                self.level_data[depth] = {'urls': [], 'texts': []}

            self.level_data[depth]['urls'].append(url)
            self.level_data[depth]['texts'].append(soup.get_text())

            if depth < self.max_depth:
                self.extract_links(soup, url, depth)

            self.save_data(depth)

    def extract_links(self, soup, base_url, current_depth):
        links_found = 0
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            full_url = urljoin(base_url, href)
            if self.is_valid_url(full_url) and self.keyword in full_url:
                if full_url not in self.visited and links_found < self.max_links:
                    self.to_visit.append((full_url, current_depth + 1))
                    links_found += 1

    def is_valid_url(self, url):
        parsed = urlparse(url)
        return bool(parsed.netloc) and bool(parsed.scheme)

    def save_data(self, depth):
        if depth in self.level_data:
            os.makedirs(f'level_{depth}', exist_ok=True)
            with open(f'level_{depth}/urls.txt', 'w', encoding='utf-8') as f_urls:
                for url in self.level_data[depth]['urls']:
                    f_urls.write(f"{url}\n")
            with open(f'level_{depth}/texts.txt', 'w', encoding='utf-8') as f_texts:
                for text in self.level_data[depth]['texts']:
                    f_texts.write(text + "\n\n")

# Usage
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os

class WebCrawler:
    def __init__(self, start_url, keyword, max_depth, max_links):
        self.start_url = start_url
        self.keyword = keyword
        self.max_depth = max_depth
        self.max_links = max_links
        self.visited = set()
        self.to_visit = [(start_url, 0)]
        self.level_data = {}

    def crawl(self):
        while self.to_visit:
            url, depth = self.to_visit.pop(0)
            if depth > self.max_depth or url in self.visited:
                continue

            try:
                response = requests.get(url)
                response.raise_for_status()
            except requests.RequestException as e:
                print(f"Failed to retrieve {url}: {e}")
                continue

            self.visited.add(url)
            soup = BeautifulSoup(response.text, 'html.parser')

            if depth not in self.level_data:
                self.level_data[depth] = {'urls': [], 'texts': []}

            self.level_data[depth]['urls'].append(url)
            self.level_data[depth]['texts'].append(soup.get_text())

            if depth < self.max_depth:
                self.extract_links(soup, url, depth)

            self.save_data(depth)

    def extract_links(self, soup, base_url, current_depth):
        links_found = 0
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            full_url = urljoin(base_url, href)
            if self.is_valid_url(full_url) and self.keyword in full_url:
                if full_url not in self.visited and links_found < self.max_links:
                    self.to_visit.append((full_url, current_depth + 1))
                    links_found += 1

    def is_valid_url(self, url):
        parsed = urlparse(url)
        return bool(parsed.netloc) and bool(parsed.scheme)

    def save_data(self, depth):
        if depth in self.level_data:
            os.makedirs(f'level_{depth}', exist_ok=True)
            with open(f'level_{depth}/urls.txt', 'w', encoding='utf-8') as f_urls:
                for url in self.level_data[depth]['urls']:
                    f_urls.write(f"{url}\n")
            with open(f'level_{depth}/texts.txt', 'w', encoding='utf-8') as f_texts:
                for text in self.level_data[depth]['texts']:
                    f_texts.write(text + "\n\n")

# Usage
start_url = "https://docs.nvidia.com/cuda/"
keyword = "docs"
max_depth = 5
max_links = 5

crawler = WebCrawler(start_url, keyword, max_depth, max_links)
crawler.crawl()
