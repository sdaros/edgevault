# Enterprise Architecture Documentation Scraper

A modular, extensible scraper for enterprise architecture documentation from multiple sources. Designed as the foundation for an Enterprise Architecture Buddy Claude Skill.

## Features

- **Multi-Source Support**: Scrape documentation from multiple enterprise sources
  - Azure Well-Architected Framework
  - SAP BTP Guidance Framework
  - Easy to add more sources

- **Modular Architecture**:
  - Base `DocumentationScraper` class with common functionality
  - Source-specific scrapers inherit and customize behavior
  - Easy to extend for new documentation sources

- **JavaScript Rendering**:
  - Support for both static and JavaScript-rendered pages
  - Uses Playwright for dynamic content
  - Configurable per-source

- **Smart Organization**:
  - Automatic categorization by pillar/topic
  - Configurable directory structure
  - Source-specific filename sanitization

- **Efficient Updates**:
  - ETag-based change detection
  - Incremental updates
  - Skip unchanged content

- **Flexible Configuration**:
  - JSON-based configuration file
  - Per-source settings
  - Command-line interface

## Architecture

```
DocumentationScraper (Base Class)
├── Common functionality (ETag caching, file management, etc.)
├── Abstract methods for source-specific behavior
│
├── AzureWellArchitectedScraper
│   ├── Static HTML pages
│   ├── Azure-specific content extraction
│   └── Pillar-based organization
│
├── SAPBTPScraper
│   ├── JavaScript-rendered pages
│   ├── SAP-specific content extraction
│   └── Category-based organization
│
└── [Your New Scraper Here]
    └── Easy to add new sources
```

## Installation

1. Install Python dependencies:

```bash
pip install -r requirements_scraper.txt
```

2. Install Playwright browsers (required for JavaScript-rendered pages):

```bash
python -m playwright install chromium
```

## Usage

### Quick Start

1. Create default configuration:

```bash
python enterprise_docs_scraper.py --create-config
```

2. Scrape all enabled sources:

```bash
python enterprise_docs_scraper.py
```

### Command-Line Options

```bash
# Scrape specific source
python enterprise_docs_scraper.py --source azure
python enterprise_docs_scraper.py --source sap_btp

# Scrape all enabled sources
python enterprise_docs_scraper.py --source all

# Use custom configuration file
python enterprise_docs_scraper.py --config my_config.json

# Create default configuration
python enterprise_docs_scraper.py --create-config
```

## Configuration

The `scraper_config.json` file controls all scraper behavior:

```json
{
  "sources": {
    "azure": {
      "enabled": true,
      "name": "Azure Well-Architected Framework",
      "base_url": "https://learn.microsoft.com/en-us/azure/well-architected/",
      "output_dir": "enterprise_docs/azure_well_architected",
      "organize_by_category": true,
      "max_depth": 3,
      "use_discovery": true,
      "use_javascript": false
    },
    "sap_btp": {
      "enabled": true,
      "name": "SAP BTP Guidance Framework",
      "base_url": "https://discovery-center.cloud.sap/guidance-framework",
      "output_dir": "enterprise_docs/sap_btp_guidance",
      "organize_by_category": true,
      "max_depth": 2,
      "use_discovery": true,
      "use_javascript": true
    }
  },
  "global": {
    "parallel_execution": false,
    "respect_robots_txt": true
  }
}
```

### Configuration Options

#### Per-Source Options

- **enabled**: Enable/disable scraping for this source
- **name**: Display name for the documentation source
- **base_url**: Starting URL for scraping
- **output_dir**: Directory to save markdown files
- **organize_by_category**: Organize files into subdirectories by category/pillar
- **max_depth**: How many levels deep to crawl for links (1-5 recommended)
- **use_discovery**: Recursively discover all linked articles
- **use_javascript**: Use Playwright to render JavaScript (required for SPAs)

#### Global Options

- **parallel_execution**: Run multiple scrapers in parallel (future feature)
- **respect_robots_txt**: Respect robots.txt directives (future feature)

## Output Structure

```
enterprise_docs/
├── azure_well_architected/
│   ├── .etag_cache.json
│   ├── index.md
│   ├── reliability/
│   │   ├── reliability.md
│   │   ├── reliability_checklist.md
│   │   └── ... (16 articles)
│   ├── security/
│   ├── cost-optimization/
│   ├── operational-excellence/
│   ├── performance-efficiency/
│   └── ... (341 total articles, ~5.6MB)
│
└── sap_btp_guidance/
    ├── .etag_cache.json
    ├── index.md
    └── ... (organized by SAP categories)
```

## Adding New Documentation Sources

Adding a new source is straightforward:

### 1. Create a New Scraper Class

```python
class MyNewScraper(DocumentationScraper):
    """Scraper for My Documentation Source."""

    def __init__(self, base_url: str = "https://docs.example.com/",
                 output_dir: str = "enterprise_docs/my_docs",
                 organize_by_category: bool = True,
                 use_javascript: bool = False):
        super().__init__("My Documentation", base_url, output_dir,
                        organize_by_category, use_javascript)

    def _extract_main_content(self, soup: BeautifulSoup) -> Optional[BeautifulSoup]:
        """Extract main content area from the page."""
        return soup.find('main') or soup.find('article')

    def _extract_article_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract article links from a page."""
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            if not href.startswith('#'):
                full_url = urljoin(base_url, href)
                if 'docs.example.com' in full_url:
                    links.append(full_url)
        return links

    def _get_category_from_url(self, url: str) -> Optional[str]:
        """Extract category from URL."""
        match = re.search(r'docs\.example\.com/([^/]+)', url)
        return match.group(1) if match else None

    def _sanitize_filename(self, url: str) -> Path:
        """Convert URL to a safe filename."""
        parsed = urlparse(url)
        path = parsed.path.strip('/').replace('/', '_')
        filename = f"{path}.md" if path else "index.md"

        category = self._get_category_from_url(url) if self.organize_by_category else None
        return Path(category) / filename if category else Path(filename)
```

### 2. Add to Configuration

```json
{
  "sources": {
    "my_source": {
      "enabled": true,
      "name": "My Documentation",
      "base_url": "https://docs.example.com/",
      "output_dir": "enterprise_docs/my_docs",
      "organize_by_category": true,
      "max_depth": 3,
      "use_discovery": true,
      "use_javascript": false
    }
  }
}
```

### 3. Update Main Function

```python
elif source_key == 'my_source':
    scraper = MyNewScraper(
        base_url=source_config['base_url'],
        output_dir=source_config['output_dir'],
        organize_by_category=source_config.get('organize_by_category', True),
        use_javascript=source_config.get('use_javascript', False)
    )
```

## Using with Claude

### Option 1: Project Knowledge

Add the entire `enterprise_docs/` directory to your Claude project's knowledge base.

### Option 2: Selective Loading

Load specific documentation sources:

```bash
# Combine all Azure articles
find enterprise_docs/azure_well_architected -name "*.md" -exec cat {} \; > azure_combined.md

# Combine specific pillar
cat enterprise_docs/azure_well_architected/reliability/*.md > azure_reliability.md
```

### Option 3: Real-time Updates

Run the scraper periodically to keep documentation up-to-date:

```bash
# Add to cron for weekly updates
0 0 * * 0 cd /path/to/project && python enterprise_docs_scraper.py --source all
```

## Troubleshooting

### Playwright Installation Issues

If you see "Executable doesn't exist" errors:

```bash
# Install browsers properly
python -m playwright install chromium

# Or install all browsers
python -m playwright install
```

### Network/Proxy Issues

Some sites (like SAP BTP) may require special network configuration:

```python
# In _fetch_content_with_js method, add proxy:
context = browser.new_context(
    user_agent='...',
    proxy={'server': 'http://proxy.example.com:8080'}
)
```

### Rate Limiting

If you encounter rate limiting:

1. Reduce `max_depth` in configuration
2. Add delays between requests:
   ```python
   import time
   time.sleep(1)  # Add after each request
   ```

### JavaScript Not Loading

Some pages may need longer wait times:

```python
# In _fetch_content_with_js, increase sleep time:
time.sleep(5)  # Wait longer for content to load
```

## Future Enhancements

- [ ] Parallel scraping support
- [ ] robots.txt compliance
- [ ] API-based documentation sources
- [ ] Incremental sync with change detection
- [ ] Export to different formats (PDF, DOCX)
- [ ] Integration with vector databases
- [ ] Claude Skill packaging

## Contributing

When adding new documentation sources:

1. Create a new scraper class inheriting from `DocumentationScraper`
2. Implement all abstract methods
3. Add source to configuration template
4. Update main function to handle new source
5. Test thoroughly
6. Update this README

## License

This script is provided as-is for educational and enterprise use.

## Support

For issues or feature requests, please open an issue in the repository.
