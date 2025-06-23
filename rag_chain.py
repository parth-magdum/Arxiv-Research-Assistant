from langchain.chains import RetrievalQA
from langchain.vectorstores import FAISS
from langchain.embeddings import SentenceTransformerEmbeddings
from groq_llm import llm

def build_rag_chain():
    
    db = FAISS.load_local(
    "faiss_arxiv",
    SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2"),
    allow_dangerous_deserialization=True
    )

    retriever = db.as_retriever(search_type="similarity", k=3)

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True,
        chain_type="stuff"
    )
    return qa_chain