from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

_vector_store = None

def get_vector_store():
    global _vector_store

    if _vector_store is None:
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        _vector_store = Chroma(
            collection_name="research_docs",
            embedding_function=embeddings,
            persist_directory="./chroma_db"
        )

    return _vector_store