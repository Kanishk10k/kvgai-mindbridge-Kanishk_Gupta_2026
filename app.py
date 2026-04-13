import streamlit as st
import requests
import os
import uuid
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# App configuration
st.set_page_config(
    page_title="MindBridge - Document Q&A",
    page_icon="📚",
    layout="wide"
)

# Configuration from environment variables with defaults
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Session state
if "context_id" not in st.session_state:
    st.session_state.context_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# UI
st.title("📚 MindBridge - Document Q&A")
st.markdown("Upload PDF documents and ask questions about their content.")

tab1, tab2 = st.tabs(["📄 Upload Document", "💬 Chat"])


# UPLOAD TAB
with tab1:
    st.header("Upload PDF Document")

    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

    if uploaded_file is not None:

        # ✅ File size validation
        if uploaded_file.size > 50 * 1024 * 1024:
            st.error("❌ File too large. Max size is 50MB.")
            st.stop()

        with st.spinner("Uploading and processing your document..."):

            temp_file_path = f"./temp_{uuid.uuid4()}_{uploaded_file.name}"

            try:
                # Save temp file
                with open(temp_file_path, "wb") as f:
                    f.write(uploaded_file.getvalue())

                # Upload to backend
                with open(temp_file_path, "rb") as f:
                    files = {
                        "file": (uploaded_file.name, f, "application/pdf")
                    }

                    st.write("Uploading to:", f"{API_BASE_URL}/upload/")  # DEBUG

                    response = requests.post(
                        f"{API_BASE_URL}/upload/",
                        files=files,
                        timeout=120
                    )

                st.write("Status Code:", response.status_code)  # DEBUG

                if response.status_code == 200:
                    result = response.json()

                    st.success("✅ Document uploaded and indexed successfully!")
                    st.json(result)

                    st.session_state.context_id = result.get("document_id")

                else:
                    st.error(f"❌ Upload failed: {response.status_code}")
                    try:
                        st.json(response.json())
                    except:
                        st.text(response.text)

            except Exception as e:
                st.error(f"❌ Error uploading document: {str(e)}")

            finally:
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)

# CHAT TAB
with tab2:
    st.header("Chat with your documents")

    # Show history
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"**You:** {msg['content']}")
        else:
            st.markdown(f"**MindBridge:** {msg['content']}")
            if "sources" in msg:
                with st.expander("Sources"):
                    for s in msg["sources"]:
                        st.write(s[:200] + "...")

    if st.session_state.context_id is None:
        st.warning("Upload a document first.")
    else:
        with st.form("chat_form", clear_on_submit=True):
            user_input = st.text_input("Ask a question")
            submit = st.form_submit_button("Send")

            if submit and user_input:

                # Reset trigger
                if any(k in user_input.lower() for k in ["reset", "clear context"]):
                    st.session_state.context_id = None
                    st.session_state.messages = []
                    st.success("Context reset!")
                    st.rerun()

                st.session_state.messages.append({
                    "role": "user",
                    "content": user_input
                })

                with st.spinner("Thinking..."):
                    try:
                        payload = {
                            "query": user_input,
                            "context_id": st.session_state.context_id
                        }

                        response = requests.post(
                            f"{API_BASE_URL}/chat/stream",
                            json=payload,
                            stream=True,
                            timeout=120
                        )

                        if response.status_code == 200:

                            placeholder = st.empty()
                            full_response = ""
                            sources = []

                            for line in response.iter_lines():
                                if line:
                                    try:
                                        chunk = json.loads(line.decode("utf-8"))

                                        if chunk.get("type") == "content":
                                            full_response += chunk["value"]
                                            placeholder.markdown(full_response + "▌")

                                        elif chunk.get("type") == "sources":
                                            sources = chunk["value"]

                                    except:
                                        pass

                            placeholder.markdown(full_response)

                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": full_response,
                                "sources": sources
                            })

                        else:
                            st.error(f"Error {response.status_code}")
                            st.text(response.text)

                    except Exception as e:
                        st.error(f"Error: {str(e)}")

                st.rerun()

    # Buttons
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Reset Context"):
            st.session_state.context_id = None
            st.session_state.messages = []
            st.success("Context reset")
            st.rerun()

    with col2:
        if st.button("Clear Chat"):
            st.session_state.messages = []
            st.success("Chat cleared")
            st.rerun()

# SIDEBAR
with st.sidebar:
    st.header("About")

    st.markdown("""
    - Upload PDF
    - Ask questions
    - Get answers with sources
    """)

    st.markdown("**Context ID:**")
    st.code(st.session_state.context_id or "None")

    # Health check
    try:
        res = requests.get(f"{API_BASE_URL}/health")
        if res.status_code == 200:
            st.success("Backend Connected")
        else:
            st.warning("Backend Issue")
    except:
        st.error("Backend Not Running")