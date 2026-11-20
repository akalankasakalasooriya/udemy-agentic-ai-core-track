from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from store import LARGE, azure_embeddings, clear, knowledge_base, open_store


def fetch_documents():
    documents = []
    for folder in sorted(path for path in knowledge_base.iterdir() if path.is_dir()):
        for file in sorted(folder.glob("*.md")):
            documents.append(Document(
                page_content=file.read_text(encoding="utf-8"),
                metadata={"source": str(file), "doc_type": folder.name},
            ))
    return documents


def create_chunks(documents):
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=200)
    return splitter.split_documents(documents)


def build():
    documents = fetch_documents()
    chunks = create_chunks(documents)
    print(f"Loaded {len(documents)} documents")
    print(f"Divided into {len(chunks)} chunks")

    clear(LARGE)
    vectorstore = open_store(LARGE, azure_embeddings())
    vectorstore.add_documents(chunks)

    count = vectorstore._collection.count()
    sample = vectorstore._collection.get(limit=1, include=["embeddings"])["embeddings"][0]
    print(f"{count} vectors, {len(sample)} dimensions, collection {LARGE}")
    return vectorstore


if __name__ == "__main__":
    build()
