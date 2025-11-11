#!/usr/bin/env python3
"""
Enterprise Architecture Documentation Scraper

A modular scraper for enterprise architecture documentation from multiple sources.
Supports Azure Well-Architected Framework, SAP BTP Guidance, and more.
"""

import os
import json
import re
import requests
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse
from typing import Dict, List, Optional, Tuple, Set
from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
from markdownify import markdownify as md

# Optional: Playwright for JavaScript-rendered pages
try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("Warning: Playwright not available. JavaScript-rendered pages will not work.")
    print("Install with: pip install playwright && playwright install chromium")


class DocumentationScraper(ABC):
    """Base class for documentation scrapers."""

    def __init__(self, name: str, base_url: str, output_dir: str,
                 organize_by_category: bool = True, use_javascript: bool = False):
        """
        Initialize the scraper.

        Args:
            name: Name of the documentation source
            base_url: The base URL of the documentation
            output_dir: Directory to save markdown files
            organize_by_category: If True, organize files into subdirectories
            use_javascript: If True, use Playwright to render JavaScript
        """
        self.name = name
        self.base_url = base_url
        self.output_dir = Path(output_dir)
        self.organize_by_category = organize_by_category
        self.use_javascript = use_javascript
        self.cache_file = self.output_dir / ".etag_cache.json"
        self.etag_cache = self._load_etag_cache()
        self.visited_urls: Set[str] = set()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

        # Check if JavaScript rendering is requested but not available
        if self.use_javascript and not PLAYWRIGHT_AVAILABLE:
            raise RuntimeError("Playwright is not installed. Install with: pip install playwright && playwright install chromium")

    def _load_etag_cache(self) -> Dict[str, str]:
        """Load ETag cache from file."""
        if self.cache_file.exists():
            with open(self.cache_file, 'r') as f:
                return json.load(f)
        return {}

    def _save_etag_cache(self):
        """Save ETag cache to file."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        with open(self.cache_file, 'w') as f:
            json.dump(self.etag_cache, f, indent=2)

    def _check_if_modified(self, url: str) -> Tuple[bool, Optional[str]]:
        """
        Check if URL has been modified using HTTP HEAD and ETag.

        Returns:
            Tuple of (is_modified, new_etag)
        """
        try:
            response = self.session.head(url, allow_redirects=True, timeout=10)
            new_etag = response.headers.get('ETag')

            if not new_etag:
                # No ETag available, consider it modified
                return True, None

            old_etag = self.etag_cache.get(url)
            is_modified = old_etag != new_etag

            return is_modified, new_etag
        except requests.RequestException as e:
            print(f"  Warning: Could not check ETag for {url}: {e}")
            return True, None

    def _fetch_content(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch content from URL."""
        if self.use_javascript:
            return self._fetch_content_with_js(url)
        else:
            return self._fetch_content_static(url)

    def _fetch_content_static(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch static content from URL using requests."""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            print(f"  Error fetching {url}: {e}")
            return None

    def _fetch_content_with_js(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch content from URL using Playwright to render JavaScript."""
        if not PLAYWRIGHT_AVAILABLE:
            print(f"  Error: Playwright not available for {url}")
            return None

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                )
                page = context.new_page()

                # Navigate and wait for content to load
                page.goto(url, wait_until='networkidle', timeout=30000)

                # Wait a bit more for dynamic content
                time.sleep(2)

                # Get the rendered HTML
                content = page.content()

                browser.close()

                return BeautifulSoup(content, 'html.parser')

        except Exception as e:
            print(f"  Error fetching {url} with JavaScript: {e}")
            return None

    def _convert_to_markdown(self, soup: BeautifulSoup, url: str) -> str:
        """Convert article HTML to markdown."""
        # Find the main content area
        main_content = self._extract_main_content(soup)

        if not main_content:
            return "# Error\n\nCould not find main content."

        # Remove navigation, footers, and other non-content elements
        for element in main_content.find_all(['nav', 'footer', 'aside']):
            element.decompose()

        # Remove script and style tags
        for element in main_content.find_all(['script', 'style']):
            element.decompose()

        # Remove common navigation classes
        for class_name in ['navigation', 'breadcrumb', 'toc', 'sidebar', 'feedback']:
            for element in main_content.find_all(class_=re.compile(class_name, re.I)):
                element.decompose()

        # Convert to markdown
        markdown_content = md(str(main_content), heading_style="ATX")

        # Add metadata header
        title = soup.find('title')
        title_text = title.get_text().strip() if title else "Untitled"

        header = f"# {title_text}\n\n"
        header += f"**Source:** {url}\n\n"
        header += f"**Documentation:** {self.name}\n\n"
        header += "---\n\n"

        # Clean up the markdown
        markdown_content = re.sub(r'\n{3,}', '\n\n', markdown_content)

        return header + markdown_content.strip()

    def _save_markdown(self, url: str, content: str):
        """Save markdown content to file."""
        relative_path = self._sanitize_filename(url)
        filepath = self.output_dir / relative_path

        # Create parent directory if needed
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"  Saved: {relative_path}")

    def _discover_all_links(self, start_url: str, max_depth: int = 3) -> List[str]:
        """
        Recursively discover all links starting from a URL.

        Args:
            start_url: The starting URL to crawl
            max_depth: Maximum depth to crawl

        Returns:
            List of all discovered URLs
        """
        all_links = set()
        to_visit = [(start_url, 0)]
        visited = set()

        print("Discovering all documentation links...")

        while to_visit:
            url, depth = to_visit.pop(0)

            # Skip if already visited or max depth reached
            if url in visited or depth > max_depth:
                continue

            visited.add(url)
            all_links.add(url)

            if depth < max_depth:
                # Fetch and extract links
                soup = self._fetch_content(url)
                if soup:
                    links = self._extract_article_links(soup, url)
                    for link in links:
                        if link not in visited:
                            to_visit.append((link, depth + 1))

                    # Show progress
                    if len(all_links) % 10 == 0:
                        print(f"  Discovered {len(all_links)} articles so far...")

        return sorted(list(all_links))

    def scrape(self, max_depth: int = 3, use_discovery: bool = True):
        """
        Main scraping method.

        Args:
            max_depth: Maximum depth for link discovery
            use_discovery: If True, recursively discover all links
        """
        print(f"\n{'='*60}")
        print(f"Starting scrape: {self.name}")
        print(f"Base URL: {self.base_url}")
        print(f"Output directory: {self.output_dir.absolute()}")
        print(f"Organization: {'By category' if self.organize_by_category else 'Flat structure'}")
        print(f"{'='*60}\n")

        # Discover all links
        if use_discovery:
            links = self._discover_all_links(self.base_url, max_depth=max_depth)
        else:
            # Fetch the main page
            print("Fetching main page...")
            soup = self._fetch_content(self.base_url)
            if not soup:
                print("Failed to fetch main page. Exiting.")
                return

            # Extract all article links
            print("Extracting article links...")
            links = self._extract_article_links(soup, self.base_url)

            # Always include the main page
            if self.base_url not in links:
                links.insert(0, self.base_url)

        print(f"\nFound {len(links)} articles to process\n")

        # Process each link
        updated_count = 0
        skipped_count = 0
        error_count = 0

        for i, url in enumerate(links, 1):
            print(f"[{i}/{len(links)}] Processing: {url}")

            # Check if modified
            is_modified, new_etag = self._check_if_modified(url)

            if not is_modified:
                print(f"  Skipped: No changes detected (ETag match)")
                skipped_count += 1
                continue

            # Fetch and convert
            soup = self._fetch_content(url)
            if not soup:
                error_count += 1
                continue

            try:
                markdown_content = self._convert_to_markdown(soup, url)
                self._save_markdown(url, markdown_content)

                # Update ETag cache
                if new_etag:
                    self.etag_cache[url] = new_etag

                updated_count += 1
            except Exception as e:
                print(f"  Error processing {url}: {e}")
                error_count += 1

        # Save ETag cache
        self._save_etag_cache()

        print(f"\n{'='*60}")
        print(f"Scraping complete: {self.name}")
        print(f"  Updated: {updated_count} articles")
        print(f"  Skipped: {skipped_count} articles (unchanged)")
        print(f"  Errors: {error_count} articles")
        print(f"  Total: {len(links)} articles")
        print(f"  Output: {self.output_dir.absolute()}")
        print(f"{'='*60}\n")

    @abstractmethod
    def _extract_main_content(self, soup: BeautifulSoup) -> Optional[BeautifulSoup]:
        """Extract the main content area from the page. Must be implemented by subclasses."""
        pass

    @abstractmethod
    def _extract_article_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract article links from a page. Must be implemented by subclasses."""
        pass

    @abstractmethod
    def _get_category_from_url(self, url: str) -> Optional[str]:
        """Extract category from URL. Must be implemented by subclasses."""
        pass

    @abstractmethod
    def _sanitize_filename(self, url: str) -> Path:
        """Convert URL to a safe filename. Must be implemented by subclasses."""
        pass


class AzureWellArchitectedScraper(DocumentationScraper):
    """Scraper for Azure Well-Architected Framework documentation."""

    def __init__(self, base_url: str = "https://learn.microsoft.com/en-us/azure/well-architected/",
                 output_dir: str = "enterprise_docs/azure_well_architected",
                 organize_by_category: bool = True,
                 use_javascript: bool = False):
        super().__init__("Azure Well-Architected Framework", base_url, output_dir,
                        organize_by_category, use_javascript)

    def _extract_main_content(self, soup: BeautifulSoup) -> Optional[BeautifulSoup]:
        """Extract main content from Azure docs page."""
        main_content = (
            soup.find('main') or
            soup.find('article') or
            soup.find('div', {'role': 'main'}) or
            soup.find('div', class_=re.compile(r'content|article|main', re.I))
        )
        if not main_content:
            main_content = soup.find('body')
        return main_content

    def _extract_article_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract article links from Azure docs page."""
        links = []
        main_content = soup.find('main') or soup.find('article') or soup

        for link in main_content.find_all('a', href=True):
            href = link['href']

            # Skip anchors
            if href.startswith('#'):
                continue

            # Make absolute URL
            full_url = urljoin(base_url, href)

            # Only include links within the well-architected documentation
            if '/azure/well-architected' in full_url:
                # Skip external domains
                parsed = urlparse(full_url)
                if 'learn.microsoft.com' not in parsed.netloc:
                    continue

                # Remove fragments and query parameters
                clean_url = full_url.split('#')[0].split('?')[0]

                # Skip if already found
                if clean_url not in links and clean_url not in self.visited_urls:
                    links.append(clean_url)

        return links

    def _get_category_from_url(self, url: str) -> Optional[str]:
        """Extract pillar name from Azure URL."""
        parsed = urlparse(url)
        path = parsed.path.strip('/')

        # Match patterns like: azure/well-architected/reliability/...
        match = re.search(r'azure/well-architected/([^/]+)', path)
        if match:
            category = match.group(1)
            # Filter out non-pillar paths
            if category not in ['', 'index', 'what-is-well-architected-framework']:
                return category
        return None

    def _sanitize_filename(self, url: str) -> Path:
        """Convert Azure URL to a safe filename with optional subdirectory."""
        parsed = urlparse(url)
        path = parsed.path.strip('/')

        # Extract category if organizing by category
        category = None
        if self.organize_by_category:
            category = self._get_category_from_url(url)

        # Remove the base path prefix if present
        if 'azure/well-architected' in path:
            path = re.sub(r'.*?azure/well-architected/?', '', path)

        # Convert to filename
        if not path or path == '':
            filename = 'index'
        else:
            filename = path.replace('/', '_')

        # Remove file extensions
        filename = re.sub(r'\.(html?|aspx?)$', '', filename)
        filename = f"{filename}.md"

        # Return path with subdirectory if category found
        if category:
            return Path(category) / filename
        return Path(filename)


class SAPBTPScraper(DocumentationScraper):
    """Scraper for SAP BTP Guidance Framework documentation."""

    def __init__(self, base_url: str = "https://discovery-center.cloud.sap/guidance-framework",
                 output_dir: str = "enterprise_docs/sap_btp_guidance",
                 organize_by_category: bool = True,
                 use_javascript: bool = True):
        super().__init__("SAP BTP Guidance Framework", base_url, output_dir,
                        organize_by_category, use_javascript)

    def _extract_main_content(self, soup: BeautifulSoup) -> Optional[BeautifulSoup]:
        """Extract main content from SAP BTP page."""
        # Try common content selectors for SAP pages
        main_content = (
            soup.find('main') or
            soup.find('article') or
            soup.find('div', {'role': 'main'}) or
            soup.find('div', class_=re.compile(r'content|article|main|guidance', re.I)) or
            soup.find('div', id=re.compile(r'content|article|main', re.I))
        )
        if not main_content:
            main_content = soup.find('body')
        return main_content

    def _extract_article_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract article links from SAP BTP page."""
        links = []
        main_content = soup.find('main') or soup.find('article') or soup

        for link in main_content.find_all('a', href=True):
            href = link['href']

            # Skip anchors and external links
            if href.startswith('#') or href.startswith('mailto:'):
                continue

            # Make absolute URL
            full_url = urljoin(base_url, href)

            # Only include links within the SAP discovery center guidance framework
            parsed = urlparse(full_url)
            if 'discovery-center.cloud.sap' in parsed.netloc and 'guidance' in full_url:
                # Remove fragments and query parameters
                clean_url = full_url.split('#')[0].split('?')[0]

                # Skip if already found
                if clean_url not in links and clean_url not in self.visited_urls:
                    links.append(clean_url)

        return links

    def _get_category_from_url(self, url: str) -> Optional[str]:
        """Extract category from SAP BTP URL."""
        parsed = urlparse(url)
        path = parsed.path.strip('/')

        # Match patterns like: guidance-framework/[category]/...
        match = re.search(r'guidance-framework/([^/]+)', path)
        if match:
            category = match.group(1)
            # Filter out common non-category paths
            if category not in ['', 'index', 'home', 'search']:
                return category
        return None

    def _sanitize_filename(self, url: str) -> Path:
        """Convert SAP BTP URL to a safe filename with optional subdirectory."""
        parsed = urlparse(url)
        path = parsed.path.strip('/')

        # Extract category if organizing by category
        category = None
        if self.organize_by_category:
            category = self._get_category_from_url(url)

        # Remove the base path prefix if present
        if 'guidance-framework' in path:
            path = re.sub(r'.*?guidance-framework/?', '', path)

        # Convert to filename
        if not path or path == '':
            filename = 'index'
        else:
            filename = path.replace('/', '_')

        # Remove file extensions
        filename = re.sub(r'\.(html?|aspx?)$', '', filename)
        filename = f"{filename}.md"

        # Return path with subdirectory if category found
        if category:
            return Path(category) / filename
        return Path(filename)


def load_config(config_file: str = "scraper_config.json") -> Dict:
    """Load scraper configuration from JSON file."""
    config_path = Path(config_file)
    if config_path.exists():
        with open(config_path, 'r') as f:
            return json.load(f)
    return {}


def save_default_config(config_file: str = "scraper_config.json"):
    """Save default configuration to JSON file."""
    default_config = {
        "sources": {
            "azure": {
                "enabled": True,
                "name": "Azure Well-Architected Framework",
                "base_url": "https://learn.microsoft.com/en-us/azure/well-architected/",
                "output_dir": "enterprise_docs/azure_well_architected",
                "organize_by_category": True,
                "max_depth": 3,
                "use_discovery": True,
                "use_javascript": False
            },
            "sap_btp": {
                "enabled": True,
                "name": "SAP BTP Guidance Framework",
                "base_url": "https://discovery-center.cloud.sap/guidance-framework",
                "output_dir": "enterprise_docs/sap_btp_guidance",
                "organize_by_category": True,
                "max_depth": 2,
                "use_discovery": True,
                "use_javascript": True
            }
        },
        "global": {
            "parallel_execution": False,
            "respect_robots_txt": True
        }
    }

    with open(config_file, 'w') as f:
        json.dump(default_config, f, indent=2)

    print(f"Created default configuration: {config_file}")
    return default_config


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Enterprise Architecture Documentation Scraper"
    )
    parser.add_argument(
        '--source',
        choices=['azure', 'sap_btp', 'all'],
        default='all',
        help='Documentation source to scrape (default: all)'
    )
    parser.add_argument(
        '--config',
        default='scraper_config.json',
        help='Configuration file (default: scraper_config.json)'
    )
    parser.add_argument(
        '--create-config',
        action='store_true',
        help='Create default configuration file and exit'
    )

    args = parser.parse_args()

    # Create config if requested
    if args.create_config:
        save_default_config(args.config)
        return

    # Load configuration
    config = load_config(args.config)
    if not config:
        print(f"Configuration file not found: {args.config}")
        print("Creating default configuration...")
        config = save_default_config(args.config)

    # Determine which sources to scrape
    sources_to_scrape = []
    if args.source == 'all':
        sources_to_scrape = [k for k, v in config.get('sources', {}).items() if v.get('enabled', False)]
    else:
        if config.get('sources', {}).get(args.source, {}).get('enabled', False):
            sources_to_scrape = [args.source]
        else:
            print(f"Source '{args.source}' is not enabled in configuration.")
            return

    # Run scrapers
    for source_key in sources_to_scrape:
        source_config = config['sources'][source_key]

        # Create appropriate scraper
        if source_key == 'azure':
            scraper = AzureWellArchitectedScraper(
                base_url=source_config['base_url'],
                output_dir=source_config['output_dir'],
                organize_by_category=source_config.get('organize_by_category', True),
                use_javascript=source_config.get('use_javascript', False)
            )
        elif source_key == 'sap_btp':
            scraper = SAPBTPScraper(
                base_url=source_config['base_url'],
                output_dir=source_config['output_dir'],
                organize_by_category=source_config.get('organize_by_category', True),
                use_javascript=source_config.get('use_javascript', True)
            )
        else:
            print(f"Unknown source: {source_key}")
            continue

        # Run scraper
        try:
            scraper.scrape(
                max_depth=source_config.get('max_depth', 3),
                use_discovery=source_config.get('use_discovery', True)
            )
        except Exception as e:
            print(f"Error scraping {source_key}: {e}")


if __name__ == "__main__":
    main()
