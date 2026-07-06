import os
from dotenv import load_dotenv
from openai import OpenAI
from pinecone import Pinecone

load_dotenv()

QUERY = "What is ADAS calibration and do yall offer it?"


def main():
    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index = pc.Index(os.getenv("PINECONE_INDEX_NAME"))

    query_embedding_response = openai_client.embeddings.create(input=[QUERY], model="text-embedding-3-small")
    query_embedding = query_embedding_response.data[0].embedding

    results = index.query(vector=query_embedding, top_k=5, include_metadata=True)

    for i, match in enumerate(results["matches"]):
        print(f"\n--- Result {i + 1} (score: {match['score']:.4f}) ---")
        print(f"Source: {match['metadata']['source']}")
        print(f"Text: {match['metadata']['text']}")


if __name__ == "__main__":
    main()
