# Azure Well-Architected Framework Documentation Scraper

A Python script that scrapes the entire Azure Well-Architected Framework documentation and saves it as markdown files for use with Claude agents or other AI assistants.

## Features

- **Comprehensive Coverage**: Scrapes the entire Well-Architected Framework including all pillars:
  - Reliability
  - Security
  - Cost Optimization
  - Operational Excellence
  - Performance Efficiency
  - Plus specialized guides (AI, Mission-Critical, Azure VMware, Oracle IaaS, SAP, etc.)
- **Organized by Pillar**: Automatically organizes files into subdirectories by pillar for easy navigation
- **Recursive Link Discovery**: Automatically discovers all related articles through recursive crawling
- **ETag-based Change Detection**: Uses HTTP HEAD requests and ETags to detect content changes
- **Incremental Updates**: Only downloads and updates articles that have changed
- **Markdown Conversion**: Converts HTML to clean markdown format
- **Metadata Tracking**: Includes source URLs and titles in each markdown file
- **Caching**: Maintains a `.etag_cache.json` file to track previous ETags

## Installation

1. Install the required dependencies:

```bash
pip install -r requirements_scraper.txt
```

## Usage

### Basic Usage

Run the script to scrape the entire Azure Well-Architected Framework:

```bash
python scrape_azure_well_architected.py
```

### Output

The script will:
1. Create an `azure_well_architected_docs/` directory
2. Save each article as a separate markdown file (organized by pillar)
3. Store ETags in `azure_well_architected_docs/.etag_cache.json`
4. Display progress and summary statistics

### Running Updates

To check for updates and refresh changed content, simply run the script again:

```bash
python scrape_azure_well_architected.py
```

The script will:
- Check each URL's ETag against the cached version
- Skip unchanged articles
- Download and update only modified articles
- Update the ETag cache

## Output Structure

The scraper organizes documentation by pillar in subdirectories:

```
azure_well_architected_docs/
├── .etag_cache.json                    # ETag cache for change detection
├── index.md                             # Main Well-Architected page
├── reliability/                         # Reliability pillar
│   ├── reliability.md
│   ├── reliability_checklist.md
│   ├── reliability_metrics.md
│   └── ... (other reliability articles)
├── security/                            # Security pillar
│   ├── security.md
│   ├── security_checklist.md
│   └── ... (other security articles)
├── cost-optimization/                   # Cost Optimization pillar
│   ├── cost-optimization.md
│   ├── cost-optimization_checklist.md
│   └── ... (other cost articles)
├── operational-excellence/              # Operational Excellence pillar
│   └── ... (operational excellence articles)
├── performance-efficiency/              # Performance Efficiency pillar
│   └── ... (performance articles)
├── ai/                                  # AI workload guidance
│   └── ... (AI-specific articles)
├── mission-critical/                    # Mission-critical guidance
│   └── ... (mission-critical articles)
└── ... (other specialized guides)
```

**Total**: ~341 articles (~5.6MB of markdown documentation)

## Configuration

You can modify the script configuration by editing the `main()` function:

```python
def main():
    # Configuration
    BASE_URL = "https://learn.microsoft.com/en-us/azure/well-architected/"
    OUTPUT_DIR = "azure_well_architected_docs"

    # Options
    ORGANIZE_BY_PILLAR = True  # Set to False for flat structure
    MAX_DEPTH = 3              # How deep to crawl links (1-5 recommended)
    USE_DISCOVERY = True       # Set to False to only scrape main page links

    scraper = AzureWellArchitectedScraper(
        BASE_URL,
        OUTPUT_DIR,
        organize_by_pillar=ORGANIZE_BY_PILLAR
    )
    scraper.scrape(max_depth=MAX_DEPTH, use_discovery=USE_DISCOVERY)
```

### Configuration Options

- **BASE_URL**: The starting URL to scrape. Use specific pillar URLs to scrape only that pillar:
  - Full framework: `https://learn.microsoft.com/en-us/azure/well-architected/`
  - Reliability only: `https://learn.microsoft.com/en-us/azure/well-architected/reliability/`
  - Security only: `https://learn.microsoft.com/en-us/azure/well-architected/security/`

- **OUTPUT_DIR**: Directory where markdown files will be saved

- **ORGANIZE_BY_PILLAR**:
  - `True` (default): Files organized in subdirectories by pillar
  - `False`: All files in a flat structure

- **MAX_DEPTH**: Controls how many levels deep to crawl for links
  - `1`: Only links from the main page
  - `2`: Links from main page + links from those pages
  - `3` (default): Three levels deep (recommended for full coverage)
  - Higher values may discover more articles but take longer

- **USE_DISCOVERY**:
  - `True` (default): Recursively discover all linked articles
  - `False`: Only scrape articles linked directly from the main page

## How It Works

1. **Recursive Link Discovery**: Starting from the base URL, recursively discovers all linked articles within the Well-Architected Framework up to the specified depth
2. **Change Detection**: For each URL, sends HTTP HEAD request to get ETag
3. **ETag Comparison**: Compares new ETags against cached values to detect changes
4. **Conditional Download**: Only downloads articles with changed or missing ETags
5. **Content Extraction**: Extracts main content from HTML, removing navigation, sidebars, and footers
6. **Markdown Conversion**: Converts HTML to clean markdown using markdownify
7. **File Organization**: Saves articles with sanitized filenames, optionally organized by pillar
8. **Cache Update**: Updates ETag cache after successful downloads for efficient future runs

## Loading Content into Claude

To use the scraped documentation with Claude:

1. **Project Knowledge**: Add the `azure_well_architected_docs/` directory (or specific pillar subdirectories) to your Claude project's knowledge base

2. **Direct Upload**: Upload specific markdown files to a conversation

3. **Batch Processing by Pillar**: Combine files from a specific pillar:
   ```bash
   # Combine all reliability articles
   cat azure_well_architected_docs/reliability/*.md > reliability_combined.md

   # Combine all security articles
   cat azure_well_architected_docs/security/*.md > security_combined.md
   ```

4. **Full Framework**: Combine all articles (note: this creates a very large file):
   ```bash
   find azure_well_architected_docs -name "*.md" -exec cat {} \; > full_framework.md
   ```

5. **Selective Loading**: Load only specific pillars relevant to your use case to manage context size

## Troubleshooting

### No ETags Available

Some pages may not return ETags. In this case, the script will download the content every time. This is expected behavior.

### Rate Limiting

If you encounter rate limiting, the script includes a User-Agent header to identify as a browser. You can add delays between requests by modifying the `scrape()` method.

### Missing Content

The script uses multiple strategies to find the main content area. If content is missing, the HTML structure may have changed. Check the `_convert_to_markdown()` method.

## Dependencies

- **requests**: HTTP library for fetching content
- **beautifulsoup4**: HTML parsing and extraction
- **markdownify**: HTML to Markdown conversion
- **lxml**: Fast HTML/XML processing (used by BeautifulSoup)

## License

This script is provided as-is for educational and personal use.
