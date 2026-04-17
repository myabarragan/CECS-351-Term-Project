# test api connection and embedding model

from dotenv import load_dotenv;
from openai import OpenAI;
import os

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key = api_key)

response = client.embeddings.create(
    model="text-embedding-3-small",
    input="hello world"
)

print(response.data[0].embedding[:5])  # print first 5 vectors
