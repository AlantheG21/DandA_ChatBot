import os
from dotenv import load_dotenv
from openai import OpenAI
from pinecone import Pinecone
from pinecone.exceptions import NotFoundException

load_dotenv()

BATCH_SIZE = 100
EMBEDDING_MODEL = "text-embedding-3-small"


def embed_and_store(chunks: list[dict]) -> int:
    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

    # Clear all existing vectors first so a run that produces fewer chunks
    # than a previous run can't leave orphaned, stale vectors behind.
    try:
        index_host = pc.describe_index(os.getenv("PINECONE_INDEX_NAME"))["host"]
        index = pc.Index(host=index_host)
        index.delete(delete_all=True)
    except NotFoundException as e:
        raise RuntimeError(
            f"Pinecone index '{os.getenv('PINECONE_INDEX_NAME')}' not found — was it deleted?"
        ) from e

    total_upserted = 0

    for i in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[i : i + BATCH_SIZE]

        texts = [chunk["text"] for chunk in batch]
        response = openai_client.embeddings.create(input=texts, model=EMBEDDING_MODEL)
        vectors = [record.embedding for record in response.data]

        records = [
            {
                "id": f"chunk-{i + j}",
                "values": vectors[j],
                "metadata": {
                    "text": batch[j]["text"],
                    "source": batch[j]["source"],
                },
            }
            for j in range(len(batch))
        ]

        index.upsert(vectors=records)
        total_upserted += len(records)
        print(f"Upserted {total_upserted}/{len(chunks)} chunks")

    return total_upserted
