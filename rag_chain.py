from langchain.chains import RetrievalQA
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain.prompts import PromptTemplate
from prompt_template import system_prompt

def build_rag_chain(llm):
    db = FAISS.load_local(
        "faiss_arxiv",
        SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2"),
        allow_dangerous_deserialization=True
    )
    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template=system_prompt
    )
    retriever = db.as_retriever(search_type="similarity", k=3)

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True,
        chain_type="stuff",
        chain_type_kwargs={"prompt": prompt}
    )
    return qa_chain