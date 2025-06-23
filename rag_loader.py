import arxiv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from graph_builder import graph

def load_and_index_arxiv(query: str, k=5):
    search = arxiv.Search(
        query=query,
        max_results=k,
        sort_by=arxiv.SortCriterion.Relevance
    )

    docs = []
    for result in search.results():
        metadata = {
            "title": result.title,
            "url": result.entry_id,
            "authors": ', '.join([author.name for author in result.authors]),
            "published": str(result.published.date())
        }

        content = result.summary.replace('\n', ' ').strip()
        doc = Document(page_content=content, metadata=metadata)
        docs.append(doc)

        # Add paper to Neo4j
        authors_list = [a.strip() for a in metadata["authors"].split(",")]
        graph.add_paper(metadata["title"], metadata["url"], authors_list, query)  # query used as topic

    # Split and embed for FAISS
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    chunks = splitter.split_documents(docs)

    embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    vectordb = FAISS.from_documents(chunks, embeddings)
    vectordb.save_local("faiss_arxiv")

    return vectordb
