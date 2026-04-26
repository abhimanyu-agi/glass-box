import os
from dotenv import load_dotenv
import psycopg2
from openai import OpenAI

load_dotenv()

# Testing Database Connection
print("Testing DB Connection")
conn = psycopg2.connect(
    host=os.getenv("POSTGRES_HOST"),
    port=os.getenv("POSTGRES_PORT"),
    dbname=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
)

with conn.cursor() as cur:
    cur.execute("SELECT COUNT(*) FROM measures_catalog;")
    count = cur.fetchone()[0]
    print(f"Postgres OK — {count} measures in catalog")
conn.close()

print("Testing OpenAI connection")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
response = client.embeddings.create(
    model="text-embedding-3-small",
    input="test",
)

dim = len(response.data[0].embedding)
print(f"  ✅ OpenAI OK — embedding has {dim} dimensions")
print("\nReady to ingest embeddings.")
                
