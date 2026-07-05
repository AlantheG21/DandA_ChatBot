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
import re
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

async def crawl_site(urls: list[str]) -> list[dict]:

    browser_cfg = BrowserConfig(headless=True)
    run_cfg = CrawlerRunConfig(
        markdown_generator=DefaultMarkdownGenerator(
            options={
                "ignore_links": True,
                "ignore_images": True,
            }
        ),
        word_count_threshold=5,
        scan_full_page=True,
        target_elements=[".dmNewParagraph", ".faq-item", ".listWidgetContainer"],
        excluded_tags=["nav", "footer", "header"],
        exclude_external_links=True,
        exclude_social_media_links=True,
        flatten_shadow_dom=True,
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

                content = result.markdown.raw_markdown
                # content = re.sub(r'\[([^\]]*)\]\([^\)]*\)', r'\1', raw)

                title = result.metadata.get("title", url)
 
                if len(content.strip()) < 100:
                    print(f"      [SKIP] Too little content at {url}")
                    continue
 
                documents.append({
                    "url": url,
                    "title": title,
                    "content": content,
                })

                #print(documents[0]["content"])

            except Exception as e:
                print(f"      [ERROR] {url}: {e}")
    
    return documents