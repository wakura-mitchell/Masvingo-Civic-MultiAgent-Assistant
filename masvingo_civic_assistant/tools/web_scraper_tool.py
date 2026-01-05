"""
Web Scraper Tool - Fetches and processes content from Masvingo City website.
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
from config.logging_config import logger
import time
from urllib.parse import urljoin, urlparse

class WebScraperTool:
    """Tool for scraping and processing web content from Masvingo City website."""

    def __init__(self, base_url: str = "https://masvingocity.org.zw/"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        logger.info("Web Scraper Tool initialized")

    def fetch_page_content(self, url: str, max_retries: int = 3) -> Optional[str]:
        """Fetch content from a specific URL."""
        for attempt in range(max_retries):
            try:
                logger.info(f"Fetching content from: {url} (attempt {attempt + 1})")
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                return response.text
            except requests.RequestException as e:
                logger.warning(f"Failed to fetch {url}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
        return None

    def extract_text_from_html(self, html_content: str) -> str:
        """Extract clean text content from HTML."""
        soup = BeautifulSoup(html_content, 'html.parser')

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Get text
        text = soup.get_text()

        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)

        return text

    def extract_links(self, html_content: str, base_url: str) -> List[str]:
        """Extract all internal links from the page."""
        soup = BeautifulSoup(html_content, 'html.parser')
        links = []

        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            full_url = urljoin(base_url, href)

            # Only include links from the same domain
            if urlparse(full_url).netloc == urlparse(base_url).netloc:
                links.append(full_url)

        return list(set(links))  # Remove duplicates

    def scrape_main_page(self) -> Dict[str, Any]:
        """Scrape the main page and extract key information."""
        html_content = self.fetch_page_content(self.base_url)
        if not html_content:
            return {"error": "Failed to fetch main page"}

        text_content = self.extract_text_from_html(html_content)
        links = self.extract_links(html_content, self.base_url)

        return {
            "url": self.base_url,
            "content": text_content,
            "links": links,
            "scraped_at": time.time()
        }

    def scrape_comprehensive(self) -> List[Dict[str, Any]]:
        """Scrape multiple key pages from the website for comprehensive information."""
        documents = []
        
        # Key pages to scrape
        key_pages = [
            {"url": self.base_url, "category": "homepage", "title": "Masvingo City Council Homepage"},
            {"url": urljoin(self.base_url, "/about-us/"), "category": "about", "title": "About Masvingo City Council"},
            {"url": urljoin(self.base_url, "/services/"), "category": "services", "title": "Council Services"},
            {"url": urljoin(self.base_url, "/departments/"), "category": "departments", "title": "Council Departments"},
            {"url": urljoin(self.base_url, "/news/"), "category": "news", "title": "Latest News and Updates"},
            {"url": urljoin(self.base_url, "/notices/"), "category": "notices", "title": "Public Notices"},
            {"url": urljoin(self.base_url, "/contact/"), "category": "contact", "title": "Contact Information"},
        ]
        
        logger.info(f"Starting comprehensive scrape of {len(key_pages)} pages")
        
        for page_info in key_pages:
            url = page_info["url"]
            logger.info(f"Scraping: {url}")
            
            html_content = self.fetch_page_content(url)
            if html_content:
                text_content = self.extract_text_from_html(html_content)
                
                # Skip if content is too short (likely an error page or redirect)
                if len(text_content.strip()) < 100:
                    logger.warning(f"Content too short for {url}, skipping")
                    continue
                
                # Extract additional structured information
                structured_data = self.extract_structured_data(html_content, page_info["category"])
                
                document = {
                    "content": text_content,
                    "metadata": {
                        "source": "masvingocity.org.zw",
                        "url": url,
                        "category": page_info["category"],
                        "title": page_info["title"],
                        "scraped_at": time.time(),
                        "type": "web_content",
                        "structured_data": structured_data
                    }
                }
                
                documents.append(document)
                logger.info(f"Successfully scraped {url}: {len(text_content)} characters")
            else:
                logger.warning(f"Failed to scrape: {url}")
        
        logger.info(f"Comprehensive scrape completed: {len(documents)} documents collected")
        return documents

    def extract_structured_data(self, html_content: str, category: str) -> Dict[str, Any]:
        """Extract structured data based on page category."""
        soup = BeautifulSoup(html_content, 'html.parser')
        structured_data = {}
        
        try:
            if category == "news":
                # Extract news articles
                articles = []
                for article in soup.find_all(['article', 'div'], class_=lambda x: x and ('news' in x.lower() or 'post' in x.lower())):
                    title = article.find(['h1', 'h2', 'h3'])
                    content = article.get_text(strip=True)
                    if title and len(content) > 50:
                        articles.append({
                            "title": title.get_text(strip=True),
                            "content": content[:500] + "..." if len(content) > 500 else content
                        })
                structured_data["articles"] = articles
                
            elif category == "services":
                # Extract services
                services = []
                for service in soup.find_all(['div', 'li'], class_=lambda x: x and ('service' in x.lower() or 'item' in x.lower())):
                    title = service.find(['h3', 'h4', 'strong'])
                    desc = service.get_text(strip=True)
                    if title and len(desc) > 20:
                        services.append({
                            "title": title.get_text(strip=True),
                            "description": desc
                        })
                structured_data["services"] = services
                
            elif category == "departments":
                # Extract departments
                departments = []
                for dept in soup.find_all(['div', 'section'], class_=lambda x: x and ('department' in x.lower() or 'dept' in x.lower())):
                    title = dept.find(['h2', 'h3'])
                    content = dept.get_text(strip=True)
                    if title and len(content) > 30:
                        departments.append({
                            "name": title.get_text(strip=True),
                            "description": content
                        })
                structured_data["departments"] = departments
                
            elif category == "contact":
                # Extract contact information
                contacts = {}
                # Look for phone numbers
                phones = soup.find_all(text=lambda x: x and ('+' in x or '263' in x or '077' in x or '078' in x))
                contacts["phones"] = [phone.strip() for phone in phones if len(phone.strip()) > 5]
                
                # Look for email addresses
                emails = soup.find_all(text=lambda x: x and '@' in x and '.' in x)
                contacts["emails"] = [email.strip() for email in emails if len(email.strip()) > 5]
                
                structured_data["contacts"] = contacts
                
        except Exception as e:
            logger.warning(f"Failed to extract structured data for category {category}: {e}")
        
        return structured_data

    def scrape_specific_pages(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Scrape multiple specific pages."""
        results = []
        for url in urls:
            html_content = self.fetch_page_content(url)
            if html_content:
                text_content = self.extract_text_from_html(html_content)
                results.append({
                    "url": url,
                    "content": text_content,
                    "scraped_at": time.time()
                })
            else:
                logger.warning(f"Failed to scrape: {url}")

        return results

    def get_recent_updates(self) -> List[Dict[str, Any]]:
        """Get recent updates and news from the website."""
        # This is a simplified implementation - in practice, you'd need to
        # identify the specific pages/sections that contain updates
        main_data = self.scrape_main_page()

        if "error" in main_data:
            return []

        # For now, return main page content as "recent updates"
        # In a real implementation, you'd parse news sections, RSS feeds, etc.
        return [main_data]

    def search_content(self, query: str, content_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Search for query in scraped content."""
        results = []
        query_lower = query.lower()

        for item in content_list:
            if query_lower in item.get("content", "").lower():
                # Create a snippet around the query
                content = item["content"]
                query_index = content.lower().find(query_lower)
                start = max(0, query_index - 100)
                end = min(len(content), query_index + len(query) + 100)
                snippet = "..." + content[start:end] + "..."

                results.append({
                    "url": item["url"],
                    "snippet": snippet,
                    "content": content
                })

        return results