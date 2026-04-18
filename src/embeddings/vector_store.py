import os
from typing import List, Dict, Any

import chromadb
from dotenv import load_dotenv
from openai import OpenAI

from src.embeddings.text_cleaning import create_snippet

CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "emails"
EMBEDDING_MODEL = "text-embedding-3-small"


def get_openai_client() -> OpenAI:
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY not found in environment.")
    return OpenAI(api_key=api_key)


def get_collection():
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    return client.get_or_create_collection(name=COLLECTION_NAME)


def embed_query(client: OpenAI, query: str) -> List[float]:
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=query
    )
    return response.data[0].embedding


def search_emails(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    #semantic search over indexed emails
    #returns a list of top matches with useful fields

    query = (query or "").strip()
    if not query:
        raise ValueError("Query cannot be empty.")

    openai_client = get_openai_client()
    collection = get_collection()

    query_embedding = embed_query(openai_client, query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )

    ids = results.get("ids", [[]])[0]
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    matches = []
    for email_id, doc, metadata, distance in zip(ids, documents, metadatas, distances):
        metadata = metadata or {}
        subject = metadata.get("subject", "")
        sender = metadata.get("sender", "")
        date = metadata.get("date", "")
        snippet = metadata.get("snippet", "") or create_snippet(doc)

        matches.append({
            "id": email_id,
            "subject": subject,
            "sender": sender,
            "date": date,
            "snippet": snippet,
            "document": doc,
            "distance": distance
        })

    return matches


if __name__ == "__main__":
    test_query = input("Enter a search query: ").strip()
    results = search_emails(test_query, top_k=5)

    print("\nTop matches:\n")
    for i, result in enumerate(results, start=1):
        print(f"{i}. Subject: {result['subject']}")
        print(f"   From: {result['sender']}")
        print(f"   Date: {result['date']}")
        print(f"   Snippet: {result['snippet']}")
        print(f"   Distance: {result['distance']}")
        print()