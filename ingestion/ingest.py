"""
Scrapes dandaautoglass.com, chunks the contents, embeds it, and stores it in Pinecone
=========================================================================================

Run:
    python ingest.py

Re-running will overwrite the existing index in Pinecone (safe to run after site updates)
"""

import os
import asyncio
from dotenv import load_dotenv

from crawler import crawl_site
from chunker import chunk_documents
from embedder import embed_and_store

load_dotenv()

TARGET_URL = "https://dandaautoglass.com/"

# Pages to crawl (can be modified to include more or fewer pages)
PAGES_TO_CRAWL = [
    TARGET_URL,
    f"{TARGET_URL}adas-recalibration/",
    f"{TARGET_URL}auto-glass-repair/",
    f"{TARGET_URL}auto-glass-replacement/",
    f"{TARGET_URL}back-glass-replacement/",
    f"{TARGET_URL}chip-repair/",
    f"{TARGET_URL}crack-repair/",
    f"{TARGET_URL}mobile-glass-repair/",
    f"{TARGET_URL}quarter-glass-repair/",
    f"{TARGET_URL}sunroof-glass-replacement/",
    f"{TARGET_URL}vent-glass-repair/",
    f"{TARGET_URL}reviews/",
    f"{TARGET_URL}faqs/",
    f"{TARGET_URL}serving-area/",
]

async def main():
    # Step 1: Crawl the site and extract content
    print("[1/3] Crawling the site...")
    documents = await crawl_site(PAGES_TO_CRAWL)
    print(f"Extracted {len(documents)} documents.")

    # Step 2: Chunk the documents
    print("[2/3] Chunking documents...")
    chunks = chunk_documents(documents)
    print(f"Created {len(chunks)} chunks.")

    # Step 3: Embed and store in Pinecone
    print("[3/3] Embedding and storing in Pinecone...")
    embed_and_store(chunks)
    print("Ingestion complete!")

if __name__ == "__main__":
    asyncio.run(main())
