import streamlit as st
from rag_chain import build_rag_chain
from rag_loader import load_and_index_arxiv

st.title("🔍 ArXiv Research Assistant [(]Powered by Arxiv and LLaMA 3(Groq API)]")

if "indexed" not in st.session_state:
    st.session_state.indexed = False

# Step 1: User chooses topic
with st.form("topic_form"):
    topic = st.text_input("Enter your research topic (e.g., quantum computing, LLMs, etc.):", "quantum computing")
    num_papers = st.slider("How many papers to load?", min_value=1, max_value=15, value=5)
    submitted = st.form_submit_button("Index Papers")

if submitted:
    with st.spinner("Fetching and embedding ArXiv papers..."):
        load_and_index_arxiv(topic, k=num_papers)
        st.success("Done indexing papers.")
        st.session_state.indexed = True

# Sidebar for graph query
with st.sidebar:
    st.markdown("### 🔎 Graph Query")
    author_name = st.text_input("Find papers by author name")
    if st.button("Search Papers by Author"):
        from graph_builder import graph  # Use the shared graph instance
        results = graph.get_papers_by_author(author_name)
        for r in results:
            st.markdown(f"- [{r['title']}]({r['url']})")

# Step 2: QA once indexing is done
if st.session_state.indexed:
    with st.form("qa_form"):
        query = st.text_input("Now enter your question:")
        ask_submitted = st.form_submit_button("Ask")
    if ask_submitted:
        qa_chain = build_rag_chain()
        result = qa_chain({"query": query})
        st.session_state.qa_result = result  # store in session_state

    # Display if exists
    if "qa_result" in st.session_state:
        result = st.session_state.qa_result
        st.markdown("### 📖 Answer")
        st.write(result["result"])

        st.markdown("### 📚 Sources")
        for idx, doc in enumerate(result["source_documents"]):
            title = doc.metadata.get("title", "Untitled")
            url = doc.metadata.get("url", "#")
            st.markdown(f"- [{title}]({url})", unsafe_allow_html=True)



