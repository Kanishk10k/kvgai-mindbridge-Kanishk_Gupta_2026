import streamlit as st
import requests
import time
import os
import uuid
import json
from io import BytesIO

# App configuration
st.set_page_config(
    page_title="MindBridge - Document Q&A",
    page_icon="📚",
    layout="wide"
)

# API Configuration
API_BASE_URL = "https://trickle-crunching-flick.ngrok-free.dev "  # Adjust if your backend runs on a different port/host

# Initialize session state
if 'context_id' not in st.session_state:
    st.session_state.context_id = None
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Custom CSS for better styling
st.markdown("""
<style>
    .upload-container {
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
    }
    .chat-container {
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .message-user {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .message-assistant {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .source-box {
        padding: 0.5rem;
        border-radius: 5px;
        margin-top: 0.5rem;
        font-size: 0.9em;
    }
</style>
""", unsafe_allow_html=True)

# Title and description
st.title("📚 MindBridge - Document Q&A")
st.markdown("Upload PDF documents and ask questions about their content.")

# Create tabs for different functionalities
tab1, tab2 = st.tabs(["📄 Upload Document", "💬 Chat"])

with tab1:
    st.header("Upload PDF Document")
    st.markdown('<div class="upload-container">', unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

    if uploaded_file is not None:
        st.info("Uploading and processing your document...")

        # Create a temporary file to save the upload with UUID to avoid collisions
        temp_file_path = f"./temp_{uuid.uuid4()}_{uploaded_file.name}"
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getvalue())

        # Upload to backend
        try:
            with open(temp_file_path, 'rb') as f:
                files = {'file': (uploaded_file.name, f, 'application/pdf')}
                response = requests.post(
    f"{API_BASE_URL}/upload/",
    files=files,
    headers={"ngrok-skip-browser-warning": "true"}
)

            if response.status_code == 200:
                result = response.json()
                st.success(f"Document uploaded successfully!")
                st.json(result)

                # Set context_id for chat (do not reset automatically on new uploads)
                st.session_state.context_id = result.get("document_id", "default_context")
            else:
                st.error(f"Upload failed with status code {response.status_code}")
                st.json(response.json())

        except Exception as e:
            st.error(f"Error uploading document: {str(e)}")
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.header("Chat with your documents")
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)

    # Display chat history
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f'<div class="message-user"><strong>You:</strong> {message["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="message-assistant"><strong>MindBridge:</strong> {message["content"]}', unsafe_allow_html=True)
            if "sources" in message:
                with st.expander("View Sources"):
                    for i, source in enumerate(message["sources"], 1):
                        # Clean and truncate source text
                        clean_source = source.strip()
                        if len(clean_source) > 200:
                            clean_source = clean_source[:200] + "..."
                        st.markdown(f'<div class="source-box"><strong>Source {i}:</strong> {clean_source}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # Chat guard - disable chat if no document is uploaded
    if st.session_state.context_id is None:
        st.warning("Upload a document first to start chatting.")
    else:
        # Chat input
        with st.form(key="chat_form", clear_on_submit=True):
            user_input = st.text_input("Ask a question about your documents:", key="user_input")
            submit_button = st.form_submit_button(label="Send")

            if submit_button and user_input:
                # Check for context reset keywords
                reset_keywords = ["reset", "refresh context", "clear context"]
                if any(keyword in user_input.lower() for keyword in reset_keywords):
                    st.session_state.context_id = None
                    st.session_state.messages = []
                    st.success("Context and chat history reset!")
                    st.rerun()

                # Add user message to history
                st.session_state.messages.append({"role": "user", "content": user_input})

                # Show thinking indicator
                with st.spinner("Thinking..."):
                    try:
                        # Prepare request payload
                        payload = {
                            "query": user_input,
                            "context_id": st.session_state.context_id
                        }

                        # Send streaming request to backend
                        response = requests.post(
    f"{API_BASE_URL}/chat/stream",
    json=payload,
    stream=True,
    headers={"ngrok-skip-browser-warning": "true"}
)

                        if response.status_code == 200:
                            # Create a placeholder for the streaming response
                            response_placeholder = st.empty()

                            # Initialize variables for streaming
                            full_response = ""
                            sources = []

                            # Stream the response
                            for line in response.iter_lines():
                                if line:
                                    try:
                                        # Parse the JSON chunk
                                        chunk_data = json.loads(line.decode('utf-8'))

                                        if chunk_data.get("type") == "content":
                                            # Add content to full response
                                            full_response += chunk_data.get("value", "")

                                            # Update the placeholder with the current response
                                            response_placeholder.markdown(f'<div class="message-assistant"><strong>MindBridge:</strong> {full_response}▌</div>', unsafe_allow_html=True)

                                        elif chunk_data.get("type") == "sources":
                                            # Store sources
                                            sources = chunk_data.get("value", [])

                                    except json.JSONDecodeError:
                                        # Handle any malformed JSON
                                        pass

                            # Clear the placeholder and show final response
                            response_placeholder.markdown(f'<div class="message-assistant"><strong>MindBridge:</strong> {full_response}</div>', unsafe_allow_html=True)

                            # Add assistant response to history
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": full_response,
                                "sources": sources
                            })
                        else:
                            st.error(f"Error: {response.status_code} - {response.text}")

                    except Exception as e:
                        st.error(f"Error communicating with backend: {str(e)}")

                # Rerun to update the chat display
                st.rerun()

    # Reset context button
    if st.button("Reset Context"):
        st.session_state.context_id = None
        st.session_state.messages = []
        st.success("Context and chat history reset!")
        st.rerun()

    # Clear chat button (only clears messages, keeps context)
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.success("Chat history cleared!")
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# Sidebar with information
with st.sidebar:
    st.header("About MindBridge")
    st.markdown("""
    MindBridge is an intelligent document-based question answering system that allows you to:

    1. Upload PDF documents
    2. Ask questions about their content
    3. Get context-grounded answers with sources

    **How it works:**
    - Documents are processed and stored in a vector database
    - Your questions are matched against relevant content
    - An LLM generates answers based on the context
    """)

    st.markdown("---")
    st.markdown("**Current Context ID:**")
    st.code(st.session_state.context_id if st.session_state.context_id else "None")

    # Health check
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            st.success("Backend: Connected")
        else:
            st.warning("Backend: Connection Issues")
    except:
        st.error("Backend: Not Connected")