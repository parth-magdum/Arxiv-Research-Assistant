import streamlit as st
from rag_chain import build_rag_chain
from rag_loader import load_and_index_arxiv

st.title("🔍 ArXiv Research Assistant [Powered by Arxiv and LLaMA 3(Groq API) via Neo4j DB]")

# Minimal chat bubble CSS
st.markdown("""
<style>
.user-bubble {
    background: #222b3a;
    color: #fff;
    border-radius: 10px;
    padding: 10px 16px;
    margin-bottom: 4px;
    display: inline-block;
    max-width: 80%;
}
.assistant-bubble {
    background: #343541;
    color: #fff;
    border-radius: 10px;
    padding: 10px 16px;
    margin-bottom: 12px;
    display: block;
    width: 100%;
    box-sizing: border-box;
}
</style>
""", unsafe_allow_html=True)

# --- Ask for API keys/passwords before anything else ---
if "groq_api_key" not in st.session_state:
    st.markdown("""
    This app lets you search, index, and chat with ArXiv papers using LLaMA 3 (via Groq API) and explore metadata relationships via Neo4j.  
    - Enter a research topic to fetch and embed relevant ArXiv papers.
    - Ask technical questions and get answers with sources.
    - Explore indexed papers and authors using the sidebar.

    You can get a Groq API key for free [here](https://console.groq.com/).
    """)
    with st.form("credentials_form"):
        st.markdown("#### Enter your credentials to start")
        groq_api_key = st.text_input("Groq API Key", type="password")
        submitted = st.form_submit_button("Start App")
    if submitted and groq_api_key:
        st.session_state.groq_api_key = groq_api_key
        st.rerun()
    st.stop()

# --- Set other config constants ---
GROQ_API_BASE = st.secrets["groq"]["api_base"]
GROQ_MODEL = st.secrets["groq"]["model"]

# Use Streamlit secrets for Neo4j
NEO4J_URI = st.secrets["neo4j"]["uri"]
NEO4J_USER = st.secrets["neo4j"]["user"]
NEO4J_PASSWORD = st.secrets["neo4j"]["password"]

if "indexed" not in st.session_state:
    st.session_state.indexed = False

if "current_papers" not in st.session_state:
    st.session_state.current_papers = []

# --- Chatbot state ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # List of (user, assistant) tuples

if "sources" not in st.session_state:
    st.session_state.sources = []  # List of source documents

# --- Lazy import and inject credentials into modules ---
import sys

# Patch groq_llm.llm with user key
import importlib
groq_llm = importlib.import_module("groq_llm")
groq_llm.llm = groq_llm.get_llm(
    api_key=st.session_state.groq_api_key,
    api_base=GROQ_API_BASE,
    model=GROQ_MODEL
)

# Patch graph_builder.graph with secrets
graph_builder = importlib.import_module("graph_builder")
graph_builder.graph = graph_builder.get_graph(
    uri=NEO4J_URI,
    user=NEO4J_USER,
    password=NEO4J_PASSWORD
)

# Step 1: User chooses topic
with st.form("topic_form"):
    topic = st.text_input("Enter your research topic:")
    num_papers = st.slider("How many papers to load?", min_value=1, max_value=15, value=5)
    submitted = st.form_submit_button("Index Papers")

if submitted:
    with st.spinner("Fetching and embedding ArXiv papers..."):
        load_and_index_arxiv(
            topic, 
            k=num_papers, 
            graph=graph_builder.graph
        )
        st.success("Done indexing papers.")
        st.session_state.indexed = True
        st.session_state.current_topic = topic
        st.session_state.current_papers = graph_builder.graph.get_papers_by_topic(topic)
        st.session_state.chat_history = []
        st.session_state.sources = []

# Sidebar for graph query
with st.sidebar:
    st.markdown("### 🔎Find Indexed Papers")

    if st.button("Show All Indexed Papers"):
        papers = st.session_state.get("current_papers", [])
        st.markdown("### 📄 All Indexed Papers (This Session)")
        if papers:
            for r in papers:
                st.markdown(f"- [{r['title']}]({r['url']})")
        else:
            st.write("No papers indexed yet in this session.")
    
    st.markdown("### 🔎Find Indexed Papers by author name")
    author_name = st.text_input("Enter author name here")
    if st.button("Search Papers by Author"):
        results = graph_builder.graph.get_papers_by_author(author_name)
        for r in results:
            st.markdown(f"- [{r['title']}]({r['url']})")

# Step 2: Chatbot QA
if st.session_state.indexed:
    st.markdown("### 💬 Chat with your research assistant")
    for i, (user_msg, assistant_msg) in enumerate(st.session_state.chat_history):
        st.markdown(
            f'<div style="display: flex; align-items: flex-start;">'
            f'<div style="flex:1"></div>'
            f'<div class="user-bubble" style="margin-left: auto;"><b></b> {user_msg}</div>'
            f'</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            f'<div class="assistant-bubble">{assistant_msg}</div>',
            unsafe_allow_html=True
        )

    with st.form("qa_form"):
        query = st.text_input("Ask any question you would like to research the topic from these papers:", key="chat_input")
        ask_submitted = st.form_submit_button("Send")
    if ask_submitted and query.strip():
        qa_chain = build_rag_chain(llm=groq_llm.llm)
        result = qa_chain({"query": query})
        st.session_state.chat_history.append((query, result["result"]))
        for doc in result["source_documents"]:
            if doc not in st.session_state.sources:
                st.session_state.sources.append(doc)
        st.rerun()

    if st.session_state.chat_history and st.session_state.sources:
        st.markdown("---")
        st.markdown("### 📚 Sources")
        shown = set()
        for doc in st.session_state.sources:
            title = doc.metadata.get("title", "Untitled")
            url = doc.metadata.get("url", "#")
            if url not in shown:
                st.markdown(f"- [{title}]({url})", unsafe_allow_html=True)
                shown.add(url)



