# run this once to build the FAISS vector DB
from rag_loader import load_and_index_arxiv

load_and_index_arxiv("quantum computing", k=5)  # You can change query/topic



