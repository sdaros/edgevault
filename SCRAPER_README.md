# Azure Well-Architected Reliability Documentation Scraper

A Python script that scrapes the Azure Well-Architected Reliability documentation and saves it as markdown files for use with Claude agents or other AI assistants.

## Features

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

Run the script to scrape all Azure reliability documentation:

```bash
python scrape_azure_reliability.py
```

### Output

The script will:
1. Create an `azure_reliability_docs/` directory
2. Save each article as a separate markdown file
3. Store ETags in `azure_reliability_docs/.etag_cache.json`
4. Display progress and summary statistics

### Running Updates

To check for updates and refresh changed content, simply run the script again:

```bash
python scrape_azure_reliability.py
```

The script will:
- Check each URL's ETag against the cached version
- Skip unchanged articles
- Download and update only modified articles
- Update the ETag cache

## Output Structure

```
azure_reliability_docs/
├── .etag_cache.json          # ETag cache for change detection
├── index.md                   # Main reliability page
├── checklist.md               # Reliability checklist
├── metrics.md                 # Reliability metrics
└── ... (other articles)
```

## Configuration

You can modify the script configuration by editing the `main()` function:

```python
def main():
    BASE_URL = "https://learn.microsoft.com/en-us/azure/well-architected/reliability/"
    OUTPUT_DIR = "azure_reliability_docs"

    scraper = AzureReliabilityScraper(BASE_URL, OUTPUT_DIR)
    scraper.scrape()
```

## How It Works

1. **Link Discovery**: Scrapes the main reliability page to find all article links
2. **Change Detection**: For each URL, sends HTTP HEAD request to get ETag
3. **Conditional Download**: Only downloads articles with changed ETags
4. **Content Extraction**: Extracts main content from HTML, removing navigation and sidebars
5. **Markdown Conversion**: Converts HTML to markdown using markdownify
6. **File Management**: Saves articles with sanitized filenames based on URLs
7. **Cache Update**: Updates ETag cache after successful downloads

## Loading Content into Claude

To use the scraped documentation with Claude:

1. **Project Knowledge**: Add the `azure_reliability_docs/` directory to your Claude project's knowledge base

2. **Direct Upload**: Upload specific markdown files to a conversation

3. **Batch Processing**: Combine multiple files for comprehensive context:
   ```bash
   cat azure_reliability_docs/*.md > combined_reliability_docs.md
   ```

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
