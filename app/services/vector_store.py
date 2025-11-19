from sentence_transformers import SentenceTransformer
import chromadb
import fitz  # PyMuPDF
import os

client = chromadb.PersistentClient(path="data/vector_db")
model = SentenceTransformer("all-MiniLM-L6-v2")

def ingest_to_vector_db(pdf_path: str, subject: str):
    try:
        doc = fitz.open(pdf_path)
        if subject in [c.name for c in client.list_collections()]:
            client.delete_collection(subject)
        
        collection = client.get_or_create_collection(name=subject)

        for page_num, page in enumerate(doc):
            text = page.get_text()
            if not text.strip():
                continue
            chunks = [text[i:i+512] for i in range(0, len(text), 512)]
            embeddings = model.encode(chunks).tolist()
            ids = [f"{os.path.basename(pdf_path)}-p{page_num}-c{i}" for i in range(len(chunks))]
            collection.add(documents=chunks, embeddings=embeddings, ids=ids)

        return True
    except Exception as e:
        print(f"Error during ingestion: {e}")
        return False

#  New function to list available subjects
def get_all_subjects():
    return [c.name for c in client.list_collections()]
