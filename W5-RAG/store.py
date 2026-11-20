import os
from pathlib import Path

import chromadb
from dotenv import load_dotenv

cwd = Path.cwd().resolve()
repo_root = next((p for p in [cwd, *cwd.parents] if (p / ".git").exists()), cwd)
load_dotenv(repo_root / ".env", override=True)

week_dir = repo_root / "W5-RAG"
knowledge_base = week_dir / "knowledge-base"
db_path = week_dir / "vector_db"

MINILM = "minilm"
LARGE = "large"
CHAT_MODEL = "gpt-4o-mini"
EMBEDDING_MODEL = "text-embedding-3-large"

_client = None


def client():
    global _client
    if _client is None:
        db_path.mkdir(parents=True, exist_ok=True)
        _client = chromadb.PersistentClient(path=str(db_path))
    return _client


def clear(name):
    db = client()
    try:
        db.delete_collection(name)
    except Exception:
        pass
    return db


def open_store(name, embeddings):
    from langchain_chroma import Chroma

    return Chroma(
        client=client(),
        collection_name=name,
        embedding_function=embeddings,
    )


def azure_embeddings():
    from langchain_openai import AzureOpenAIEmbeddings

    return AzureOpenAIEmbeddings(
        azure_endpoint=os.getenv("GPT_ENDPOINT"),
        api_key=os.getenv("GPT_KEY"),
        api_version=os.getenv("GPT_API_VERSION"),
        azure_deployment=EMBEDDING_MODEL,
        model=EMBEDDING_MODEL,
        chunk_size=64,
    )


def azure_chat(temperature=0):
    from langchain_openai import AzureChatOpenAI

    return AzureChatOpenAI(
        azure_endpoint=os.getenv("GPT_ENDPOINT"),
        api_key=os.getenv("GPT_KEY"),
        api_version=os.getenv("GPT_API_VERSION"),
        azure_deployment=CHAT_MODEL,
        temperature=temperature,
        timeout=120,
    )
