import os
from dotenv import load_dotenv
from openai import OpenAI
from pinecone import NotFoundException, Pinecone

load_dotenv()

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

# Resolve the index host once at startup instead of on every request —
# pc.Index(name=...) does an implicit describe_index lookup internally each
# time it's called, which would otherwise happen on every /chat request.
try:
    index_host = pc.describe_index(os.getenv("PINECONE_INDEX_NAME")).host

except NotFoundException as e:
    raise RuntimeError(
        f"Pinecone index '{os.getenv('PINECONE_INDEX_NAME')}' not found - was it deleted?."
    ) from e

index = pc.Index(host=index_host)

def retrieve_chunks(query: str, top_k: int = 5) -> list[dict]:
    query_embedding_response = openai_client.embeddings.create(
        input=query, model="text-embedding-3-small"
    )
    query_embedding = query_embedding_response.data[0].embedding

    query_response = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True
    )

    return [
        {"text": match["metadata"]["text"], "source": match["metadata"]["source"]}
        for match in query_response["matches"]
    ]