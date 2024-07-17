# import requests
# from bs4 import BeautifulSoup
# from urllib.parse import urljoin, urlparse
# import time

# class WebCrawler:
#     def __init__(self, base_url, max_depth):
#         self.base_url = base_url
#         self.max_depth = max_depth
#         self.visited = set()

#     def fetch_content(self, url):
#         try:
#             response = requests.get(url)
#             if response.status_code == 200:
#                 return response.content
#         except Exception as e:
#             print(f"Failed to fetch {url}: {e}")
#         return None

#     def get_links(self, soup, base_url):
#         links = set()
#         for a_tag in soup.find_all('a', href=True):
#             href = a_tag.get('href')
#             full_url = urljoin(base_url, href)
#             if self.is_valid_url(full_url):
#                 links.add(full_url)
#         return links

#     def is_valid_url(self, url):
#         parsed_url = urlparse(url)
#         return bool(parsed_url.netloc) and bool(parsed_url.scheme)

#     def crawl(self, url, depth):
#         if url in self.visited or depth > self.max_depth:
#             return
        
#         print(f"Crawling: {url} at depth: {depth}")
#         self.visited.add(url)
#         content = self.fetch_content(url)

#         if content:
#             soup = BeautifulSoup(content, 'html.parser')
#             links = self.get_links(soup, url)

#             for link in links:
#                 self.crawl(link, depth + 1)

# if __name__ == "__main__":
#     base_url = "https://docs.nvidia.com/cuda/"
#     max_depth = 5
#     crawler = WebCrawler(base_url, max_depth)
#     crawler.crawl(base_url, 0)


# import requests
# from bs4 import BeautifulSoup
# from urllib.parse import urljoin, urlparse
# import json
# import time

# class WebCrawler:
#     def __init__(self, base_url, max_depth):
#         self.base_url = base_url
#         self.max_depth = max_depth
#         self.visited = set()
#         self.queue = [(base_url, 0)]  # (url, depth)
#         self.result = {}

#     def fetch_content(self, url):
#         try:
#             response = requests.get(url)
#             if response.status_code == 200:
#                 return response.content
#         except Exception as e:
#             print(f"Failed to fetch {url}: {e}")
#         return None

#     def get_links(self, soup, base_url):
#         links = set()
#         for a_tag in soup.find_all('a', href=True):
#             href = a_tag.get('href')
#             full_url = urljoin(base_url, href)
#             if self.is_valid_url(full_url):
#                 links.add(full_url)
#         return links

#     def is_valid_url(self, url):
#         parsed_url = urlparse(url)
#         return bool(parsed_url.netloc) and bool(parsed_url.scheme)

#     def crawl(self):
#         while self.queue:
#             url, depth = self.queue.pop(0)
#             if url in self.visited or depth > self.max_depth:
#                 continue
            
#             print(f"Crawling: {url} at depth: {depth}")
#             self.visited.add(url)
#             content = self.fetch_content(url)

#             if content:
#                 soup = BeautifulSoup(content, 'html.parser')
#                 links = self.get_links(soup, url)
#                 self.result[url] = list(links)

#                 for link in links:
#                     if link not in self.visited:
#                         self.queue.append((link, depth + 1))

#     def save_to_json(self, file_path):
#         with open(file_path, 'w') as file:
#             json.dump(self.result, file, indent=4)

# if __name__ == "__main__":
#     base_url = "https://docs.nvidia.com/cuda/"
#     max_depth = 5
#     crawler = WebCrawler(base_url, max_depth)
#     crawler.crawl()
#     crawler.save_to_json("crawled_links.json")

# 


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
