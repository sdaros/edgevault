#!/usr/bin/env python3
"""
Azure Well-Architected Reliability Documentation Scraper

This script scrapes the Azure Well-Architected Reliability documentation
and saves it as markdown files. It uses ETags to detect changes and only
updates files when content has changed.
"""

import os
import json
import re
import requests
from pathlib import Path
from urllib.parse import urljoin, urlparse
from typing import Dict, List, Optional, Tuple
from bs4 import BeautifulSoup
from markdownify import markdownify as md


class AzureReliabilityScraper:
    def __init__(self, base_url: str, output_dir: str = "azure_reliability_docs"):
        """
        Initialize the scraper.

        Args:
            base_url: The base URL of the Azure reliability documentation
            output_dir: Directory to save markdown files
        """
        self.base_url = base_url
        self.output_dir = Path(output_dir)
        self.cache_file = self.output_dir / ".etag_cache.json"
        self.etag_cache = self._load_etag_cache()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

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

    def _sanitize_filename(self, url: str) -> str:
        """Convert URL to a safe filename."""
        parsed = urlparse(url)
        path = parsed.path.strip('/')

        # Remove the base path prefix if present
        if path.startswith('azure/well-architected/reliability'):
            path = path.replace('azure/well-architected/reliability', '', 1).strip('/')

        # Convert to filename
        if not path or path == '':
            filename = 'index'
        else:
            filename = path.replace('/', '_')

        # Remove file extensions
        filename = re.sub(r'\.(html?|aspx?)$', '', filename)

        return f"{filename}.md"

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
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            print(f"  Error fetching {url}: {e}")
            return None

    def _extract_article_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract all article links from the main page."""
        links = []

        # Find the main content area
        main_content = soup.find('main') or soup.find('article') or soup

        # Look for links in various structures
        for link in main_content.find_all('a', href=True):
            href = link['href']

            # Skip anchors, external links, and non-reliability links
            if href.startswith('#'):
                continue

            # Make absolute URL
            full_url = urljoin(base_url, href)

            # Only include links within the reliability documentation
            if '/azure/well-architected/reliability' in full_url:
                # Remove fragments and query parameters
                clean_url = full_url.split('#')[0].split('?')[0]
                if clean_url not in links:
                    links.append(clean_url)

        return links

    def _convert_to_markdown(self, soup: BeautifulSoup, url: str) -> str:
        """Convert article HTML to markdown."""
        # Find the main content area
        main_content = (
            soup.find('main') or
            soup.find('article') or
            soup.find('div', {'role': 'main'}) or
            soup.find('div', class_=re.compile(r'content|article|main', re.I))
        )

        if not main_content:
            main_content = soup.find('body')

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
        header += "---\n\n"

        # Clean up the markdown
        markdown_content = re.sub(r'\n{3,}', '\n\n', markdown_content)

        return header + markdown_content.strip()

    def _save_markdown(self, url: str, content: str):
        """Save markdown content to file."""
        filename = self._sanitize_filename(url)
        filepath = self.output_dir / filename

        self.output_dir.mkdir(parents=True, exist_ok=True)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"  Saved: {filename}")

    def scrape(self):
        """Main scraping method."""
        print(f"Starting scrape of {self.base_url}")
        print(f"Output directory: {self.output_dir.absolute()}\n")

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

        print(f"Found {len(links)} articles to process\n")

        # Process each link
        updated_count = 0
        skipped_count = 0

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
                continue

            markdown_content = self._convert_to_markdown(soup, url)
            self._save_markdown(url, markdown_content)

            # Update ETag cache
            if new_etag:
                self.etag_cache[url] = new_etag

            updated_count += 1

        # Save ETag cache
        self._save_etag_cache()

        print(f"\n{'='*60}")
        print(f"Scraping complete!")
        print(f"  Updated: {updated_count} articles")
        print(f"  Skipped: {skipped_count} articles (unchanged)")
        print(f"  Total: {len(links)} articles")
        print(f"  Output: {self.output_dir.absolute()}")
        print(f"{'='*60}")


def main():
    """Main entry point."""
    # Configuration
    BASE_URL = "https://learn.microsoft.com/en-us/azure/well-architected/reliability/"
    OUTPUT_DIR = "azure_reliability_docs"

    # Create and run scraper
    scraper = AzureReliabilityScraper(BASE_URL, OUTPUT_DIR)
    scraper.scrape()


if __name__ == "__main__":
    main()
