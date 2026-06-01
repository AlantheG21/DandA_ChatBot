"""
Uses Crawl4AI to scrape a list of URLs and return clean markdown content.
Each page becomes one Document dict:
  {
    "url": str,
    "title": str,
    "content": str,   # clean markdown
  }
"""

import asyncio
from unittest import result
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

async def crawl_site(urls: list[str]) -> list[dict]:

    browser_cfg = BrowserConfig(headless=True)
    run_cfg = CrawlerRunConfig(
        markdown_generator=DefaultMarkdownGenerator(
            options={
                "ignore_links": False,
                "ignore_images": True,
            }
        ),
        wait_for="body",
        page_timeout=15000,
    )

    documents = []

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        for url in urls:
            print(f"Crawling {url}...")

            try:
                result = await crawler.arun(url=url, config=run_cfg)
                if not result.success:
                    print(f"      [WARN] Failed to crawl {url}: {result.error_message}")
                    continue

                content = result.markdown.raw_markdown  # clean markdown content
                title = result.metadata.get("title", url)
 
                if len(content.strip()) < 100:
                    print(f"      [SKIP] Too little content at {url}")
                    continue
 
                documents.append({
                    "url": url,
                    "title": title,
                    "content": content,
                })

            except Exception as e:
                print(f"      [ERROR] {url}: {e}")
    
    return documents