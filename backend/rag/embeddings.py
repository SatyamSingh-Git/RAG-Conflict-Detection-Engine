from langchain_huggingface import HuggingFaceEmbeddings

# Using BAAI/bge-small-en-v1.5 which is fast and outputs 384 dimensions
embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")

def get_embedding(text: str):
    return embeddings.embed_query(text)

def get_embeddings(texts: list[str]):
    return embeddings.embed_documents(texts)
