import json
import os
from pathlib import Path
from typing import List, Dict

import chromadb
from dotenv import load_dotenv
from openai import OpenAI

from src.embeddings.text_cleaning import (
    build_email_document,
    clean_email_body,
    create_snippet,
)

EMAILS_JSON_PATH = Path("data/emails.json")
CHROMA_DIR = Path("chroma_db")
COLLECTION_NAME = "emails"
EMBEDDING_MODEL = "text-embedding-3-small"
BATCH_SIZE = 100
MAX_BODY_CHARS = 12000


def load_emails(path: Path) -> List[Dict]:
    #load emails from JSON file

    if not path.exists():
        raise FileNotFoundError(f"Could not find email file: {path}")

    with open(path, "r", encoding="utf-8") as f:
        emails = json.load(f)

    if not isinstance(emails, list):
        raise ValueError("emails.json must contain a list of email objects.")

    return emails


def get_openai_client() -> OpenAI:
    #create OpenAI client from environment variable

    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY not found in environment.")
    return OpenAI(api_key=api_key)


def get_chroma_collection():
    #create or open a persistent Chroma collection

    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    collection = client.get_or_create_collection(name=COLLECTION_NAME)
    return collection


def prepare_records(emails: List[Dict]) -> List[Dict]:
    #clean and normalize emails into records ready for embedding and storage

    prepared = []

    for email in emails:
        email_id = str(email.get("id", "")).strip()
        if not email_id:
            continue

        subject = email.get("subject", "") or ""
        sender = email.get("sender", "") or ""
        date = email.get("date", "") or ""
        raw_body = email.get("body", "") or ""
        cleaned_body = clean_email_body(raw_body)

        #trim the very long emails so they do not exceed the embedding model limits
        if len(cleaned_body) > MAX_BODY_CHARS:
            cleaned_body = cleaned_body[:MAX_BODY_CHARS]

        document = build_email_document({
            "subject": subject,
            "sender": sender,
            "date": date,
            "body": cleaned_body,
        })

        snippet = create_snippet(cleaned_body)

        prepared.append({
            "id": email_id,
            "document": document,
            "metadata": {
                "subject": subject,
                "sender": sender,
                "date": date,
                "snippet": snippet,
            }
        })

    return prepared


def embed_texts(client: OpenAI, texts: List[str]) -> List[List[float]]:
    #generate embeddings for a batch of texts

    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=texts
    )
    return [item.embedding for item in response.data]


def clear_collection(collection) -> None:
    #remove all existing documents from the collection

    existing = collection.get(include=[])
    existing_ids = existing.get("ids", [])
    if existing_ids:
        collection.delete(ids=existing_ids)


def index_emails(rebuild: bool = True) -> None:
    #main indexing pipeline:
    #1.load emails
    #2.clean them
    #3.generate embeddings
    #4.store in Chroma

    print("Loading emails...")
    emails = load_emails(EMAILS_JSON_PATH)
    print(f"Loaded {len(emails)} raw emails.")

    print("Preparing records...")
    records = prepare_records(emails)
    print(f"Prepared {len(records)} emails for embedding.")

    if not records:
        raise ValueError("No valid email records found to index.")

    print("Initializing clients...")
    openai_client = get_openai_client()
    collection = get_chroma_collection()

    if rebuild:
        print("Clearing existing Chroma collection...")
        clear_collection(collection)

    print("Embedding and storing emails in batches...")
    for start in range(0, len(records), BATCH_SIZE):
        batch = records[start:start + BATCH_SIZE]

        ids = [r["id"] for r in batch]
        documents = [r["document"] for r in batch]
        metadatas = [r["metadata"] for r in batch]

        embeddings = embed_texts(openai_client, documents)

        collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings
        )

        print(f"Indexed batch {start // BATCH_SIZE + 1} "
              f"({start + 1}-{start + len(batch)} of {len(records)})")

    print(f"Done. Indexed {len(records)} emails into Chroma collection '{COLLECTION_NAME}'.")


if __name__ == "__main__":
    index_emails(rebuild=True)