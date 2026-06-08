from langchain_text_splitters import RecursiveCharacterTextSplitter


def chunk_documents(pages: list[dict]) -> list[dict]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=150,
    )

    chunks = []
    for page in pages:
        url = page["url"]
        text = page["content"]

        if len(text) < 50:
            continue

        for chunk_text in splitter.split_text(text):
            chunks.append({"text": chunk_text, "source": url})

    return chunks
