import os
from dotenv import load_dotenv
from openai import OpenAI
from pinecone import Pinecone

load_dotenv()

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

def retrieve_chunks(query: str, top_k: int = 5) -> list[dict]:
    index = pc.Index(os.getenv("PINECONE_INDEX_NAME"))

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