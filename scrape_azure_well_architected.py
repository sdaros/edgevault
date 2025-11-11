#!/usr/bin/env python3
"""
Azure Well-Architected Framework Documentation Scraper

This script scrapes the Azure Well-Architected Framework documentation
and saves it as markdown files. It uses ETags to detect changes and only
updates files when content has changed.
"""

import os
import json
import re
import requests
from pathlib import Path
from urllib.parse import urljoin, urlparse
from typing import Dict, List, Optional, Tuple, Set
from bs4 import BeautifulSoup
from markdownify import markdownify as md


class AzureWellArchitectedScraper:
    def __init__(self, base_url: str, output_dir: str = "azure_well_architected_docs", organize_by_pillar: bool = True):
        """
        Initialize the scraper.

        Args:
            base_url: The base URL of the Azure Well-Architected documentation
            output_dir: Directory to save markdown files
            organize_by_pillar: If True, organize files into subdirectories by pillar
        """
        self.base_url = base_url
        self.output_dir = Path(output_dir)
        self.organize_by_pillar = organize_by_pillar
        self.cache_file = self.output_dir / ".etag_cache.json"
        self.etag_cache = self._load_etag_cache()
        self.visited_urls: Set[str] = set()
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

    def _get_pillar_from_url(self, url: str) -> Optional[str]:
        """Extract pillar name from URL."""
        parsed = urlparse(url)
        path = parsed.path.strip('/')

        # Match patterns like: azure/well-architected/reliability/...
        match = re.search(r'azure/well-architected/([^/]+)', path)
        if match:
            pillar = match.group(1)
            # Filter out non-pillar paths
            if pillar not in ['', 'index', 'what-is-well-architected-framework']:
                return pillar
        return None

    def _sanitize_filename(self, url: str) -> Path:
        """Convert URL to a safe filename with optional subdirectory."""
        parsed = urlparse(url)
        path = parsed.path.strip('/')

        # Extract pillar if organizing by pillar
        pillar = None
        if self.organize_by_pillar:
            pillar = self._get_pillar_from_url(url)

        # Remove the base path prefix if present
        if 'azure/well-architected' in path:
            # Remove base prefix
            path = re.sub(r'.*?azure/well-architected/?', '', path)

        # Convert to filename
        if not path or path == '':
            filename = 'index'
        else:
            filename = path.replace('/', '_')

        # Remove file extensions
        filename = re.sub(r'\.(html?|aspx?)$', '', filename)
        filename = f"{filename}.md"

        # Return path with subdirectory if pillar found
        if pillar:
            return Path(pillar) / filename
        return Path(filename)

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
        """Extract all article links from a page recursively."""
        links = []

        # Find the main content area
        main_content = soup.find('main') or soup.find('article') or soup

        # Look for links in various structures
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
        relative_path = self._sanitize_filename(url)
        filepath = self.output_dir / relative_path

        # Create parent directory if needed
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"  Saved: {relative_path}")

    def scrape(self, max_depth: int = 3, use_discovery: bool = True):
        """
        Main scraping method.

        Args:
            max_depth: Maximum depth for link discovery
            use_discovery: If True, recursively discover all links. If False, only scrape links from main page.
        """
        print(f"Starting scrape of {self.base_url}")
        print(f"Output directory: {self.output_dir.absolute()}")
        print(f"Organization: {'By pillar' if self.organize_by_pillar else 'Flat structure'}\n")

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
        print(f"Scraping complete!")
        print(f"  Updated: {updated_count} articles")
        print(f"  Skipped: {skipped_count} articles (unchanged)")
        print(f"  Errors: {error_count} articles")
        print(f"  Total: {len(links)} articles")
        print(f"  Output: {self.output_dir.absolute()}")
        print(f"{'='*60}")


def main():
    """Main entry point."""
    # Configuration
    BASE_URL = "https://learn.microsoft.com/en-us/azure/well-architected/"
    OUTPUT_DIR = "azure_well_architected_docs"

    # Options
    ORGANIZE_BY_PILLAR = True  # Set to False for flat structure
    MAX_DEPTH = 3  # How deep to crawl links
    USE_DISCOVERY = True  # Set to False to only scrape main page links

    # Create and run scraper
    scraper = AzureWellArchitectedScraper(
        BASE_URL,
        OUTPUT_DIR,
        organize_by_pillar=ORGANIZE_BY_PILLAR
    )
    scraper.scrape(max_depth=MAX_DEPTH, use_discovery=USE_DISCOVERY)


if __name__ == "__main__":
    main()
