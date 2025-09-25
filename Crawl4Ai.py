import asyncio
import json
import zipfile
import time
from pathlib import Path
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy
from crawl4ai.content_scraping_strategy import LXMLWebScrapingStrategy

async def main():
    start_time = time.time()

    # Configure a 2-level deep crawl
    config = CrawlerRunConfig(
        deep_crawl_strategy=BFSDeepCrawlStrategy(
            max_depth=2,
            max_pages=350,
            include_external=False
        ),
        scraping_strategy=LXMLWebScrapingStrategy(),
        verbose=True
    )

    async with AsyncWebCrawler() as crawler:
        results = await crawler.arun("https://www.wikipedia.org", config=config)

        print(f"Crawled {len(results)} pages in total")

        output_dir = Path("crawl_output")
        output_dir.mkdir(exist_ok=True)

        for i, result in enumerate(results):
            # Use 'html' attribute which exists in CrawlResult
            data = {
                "url": result.url,
                "depth": result.metadata.get("depth", 0),
                "content": getattr(result, "html", "")  # safe fallback
            }
            with open(output_dir / f"page_{i+1}.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        # Zip all JSON files
        zip_path = "crawl_results.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for file in output_dir.iterdir():
                zipf.write(file, arcname=file.name)

        elapsed_time = time.time() - start_time
        print(f"Saved results to {zip_path}")
        print(f"Total crawl time: {elapsed_time:.2f} seconds")

if __name__ == "__main__":
    asyncio.run(main())
