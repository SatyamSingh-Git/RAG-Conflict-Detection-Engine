import os
import json
import PyPDF2
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from rag.embeddings import get_embeddings
from rag.pinecone_utils import get_pinecone_index

load_dotenv()

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")

def extract_text_pypdf(file_path):
    text = ""
    with open(file_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"
    return text

def parse_txt_md(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    metadata = {}
    if content.startswith("Metadata: "):
        lines = content.split("\n")
        try:
            metadata = json.loads(lines[0].replace("Metadata: ", ""))
            content = "\n".join(lines[1:]).strip()
        except:
            pass
    return content, metadata

def process_file(file_path, filename):
    print(f"Processing {filename}...")
    ext = filename.split('.')[-1].lower()
    content = ""
    metadata = {"filename": filename, "source": file_path}
    
    if ext == "pdf":
        content = extract_text_pypdf(file_path)
    elif ext in ["txt", "md"]:
        content, meta = parse_txt_md(file_path)
        metadata.update(meta)
    else:
        print(f"Skipping {filename}: Unsupported extension")
        return []
        
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.create_documents([content], metadatas=[metadata])
    return chunks

def ingest_all():
    docs = []
    for f in os.listdir(DATA_DIR):
        file_path = os.path.join(DATA_DIR, f)
        if os.path.isfile(file_path):
            docs.extend(process_file(file_path, f))
            
    if not docs:
        print("No documents found.")
        return

    print(f"Total chunks generated: {len(docs)}")
    
    # Extract text and prepare for pinecone
    texts = [d.page_content for d in docs]
    print("Generating embeddings...")
    vectors = get_embeddings(texts)
    
    print("Upserting to Pinecone...")
    index = get_pinecone_index()
    
    records = []
    for i, (doc, vec) in enumerate(zip(docs, vectors)):
        meta = doc.metadata.copy()
        meta["text"] = doc.page_content
        records.append({
            "id": f"{meta['filename']}_chunk_{i}",
            "values": vec,
            "metadata": meta
        })
        
    # Batch upsert
    batch_size = 100
    for i in range(0, len(records), batch_size):
        batch = records[i:i+batch_size]
        index.upsert(vectors=batch)
        print(f"Upserted batch {i//batch_size + 1}")
        
    print("Ingestion complete.")

if __name__ == "__main__":
    ingest_all()
