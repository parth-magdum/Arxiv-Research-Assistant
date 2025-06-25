import streamlit as st
from rag_chain import build_rag_chain
from rag_loader import load_and_index_arxiv

st.title("🔍 ArXiv Research Assistant [Powered by Arxiv and LLaMA 3(Groq API)]")

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

if "indexed" not in st.session_state:
    st.session_state.indexed = False

if "current_papers" not in st.session_state:
    st.session_state.current_papers = []

# --- Chatbot state ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # List of (user, assistant) tuples

if "sources" not in st.session_state:
    st.session_state.sources = []  # List of source documents

# Step 1: User chooses topic
with st.form("topic_form"):
    topic = st.text_input("Enter your research topic:")
    num_papers = st.slider("How many papers to load?", min_value=1, max_value=15, value=5)
    submitted = st.form_submit_button("Index Papers")

if submitted:
    with st.spinner("Fetching and embedding ArXiv papers..."):
        load_and_index_arxiv(topic, k=num_papers)
        st.success("Done indexing papers.")
        st.session_state.indexed = True
        # Query graph db for papers with this topic and store in session
        from graph_builder import graph
        st.session_state.current_topic = topic
        st.session_state.current_papers = graph.get_papers_by_topic(topic)
        # Reset chat and sources when topic changes
        st.session_state.chat_history = []
        st.session_state.sources = []

# Sidebar for graph query
with st.sidebar:
    st.markdown("### 🔎Find Indexed Papers")

    # --- Show only session's indexed papers ---
    if st.button("Show All Indexed Papers"):
        papers = st.session_state.get("current_papers", [])
        st.markdown("### 📄 All Indexed Papers (This Session)")
        if papers:
            for r in papers:
                st.markdown(f"- [{r['title']}]({r['url']})")
        else:
            st.write("No papers indexed yet in this session.")
    
    st.markdown("### 🔎Find Indexed Papers by author name")
    # --- Search by author name ---
    author_name = st.text_input("Enter author name here")
    if st.button("Search Papers by Author"):
        from graph_builder import graph  # Use the shared graph instance
        results = graph.get_papers_by_author(author_name)
        for r in results:
            st.markdown(f"- [{r['title']}]({r['url']})")

# Step 2: Chatbot QA
if st.session_state.indexed:
    st.markdown("### 💬 Chat with your research assistant")
    # Display chat history
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
        qa_chain = build_rag_chain()
        result = qa_chain({"query": query})
        # Append to chat history
        st.session_state.chat_history.append((query, result["result"]))
        # Collect sources (accumulate unique sources)
        for doc in result["source_documents"]:
            if doc not in st.session_state.sources:
                st.session_state.sources.append(doc)
        st.rerun()  # Refresh to show new chat

    # Show sources only at the end of the conversation (if any exchanges)
    if st.session_state.chat_history and st.session_state.sources:
        st.markdown("---")
        st.markdown("### 📚 Sources (for this session)")
        shown = set()
        for doc in st.session_state.sources:
            title = doc.metadata.get("title", "Untitled")
            url = doc.metadata.get("url", "#")
            # Avoid duplicate links
            if url not in shown:
                st.markdown(f"- [{title}]({url})", unsafe_allow_html=True)
                shown.add(url)



