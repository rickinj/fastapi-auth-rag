from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from sentence_transformers import SentenceTransformer
import os
import shutil


embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

embedding_function = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

BASE_PATH = "faiss_indexes"
os.makedirs(BASE_PATH, exist_ok=True)

def chunk_text(text: str):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size = 800,
        chunk_overlap = 150
    )
    return splitter.split_text(text)

def create_index(doc_id: int, text: str):
    chunks = chunk_text(text)
    embeddings = embedding_model.encode(chunks)

    path = os.path.join(BASE_PATH, f"doc_{doc_id}")

    db = FAISS.from_embeddings(list(zip(chunks, embeddings)),embedding_function)
    
    db.save_local(path)

def load_index(doc_id: int):
    path = os.path.join(BASE_PATH, f"doc_{doc_id}")

    if not os.path.exists(path):
        raise Exception(f"No Index Found for doc: {doc_id}")
    
    return FAISS.load_local(
        path,
        embeddings = embedding_function,
        allow_dangerous_deserialization = True
    )

def rag_search(doc_id: int, query: str):
    db = load_index(doc_id)

    docs = db.similarity_search(query, k=5)

    results = [doc.page_content for doc in docs]

    return results

def search_all_documents(query: str):
    all_results = []

    for folder in os.listdir(BASE_PATH):
        path = os.path.join(BASE_PATH, folder)

        if not os.path.isdir(path):
            continue

        db = FAISS.load_local(
            path,
            embeddings = embedding_function,
            allow_dangerous_deserialization = True
        )

        docs = db.similarity_search(query, k=5)

        for d in docs:
            all_results.append({
                "doc_id": folder.replace("doc_",""),
                "text": d.page_content
            })
    return all_results[:3]

def delete_index(doc_id: int):
    path = os.path.join(BASE_PATH, f"doc_{doc_id}")

    if os.path.exists(path):
        shutil.rmtree(path)
        return True
    return False