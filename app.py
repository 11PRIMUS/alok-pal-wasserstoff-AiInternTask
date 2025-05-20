import streamlit as st
from dotenv import load_dotenv
import os
from pathlib import Path
from utils.ocr_doc import get_doc
from utils.database import init_vector_store, add_documnent, get_all_doc_ids
from utils.qa_system import query_document, analyze_themes

load_dotenv()

NEBIUS_API_KEY = os.getenv("NEBIUS_API_KEY")
if not NEBIUS_API_KEY:
    st.error("nebius key not found")
    st.stop()

UPLOAD_DIR=Path("uploaded_docs")
UPLOAD_DIR.mkdir(exist_ok=True)
VECTOR_STORE_PATH="./vector_store_db"

try:
    vector_store=init_vector_store(VECTOR_STORE_PATH, NEBIUS_API_KEY)
    st.sidebar.success("vector store ")
except Exception as e:
    st.error(f"failed to init vector store{e}")
    st.stop()
    
st.title("Document Query and Analysis with Nebius AI")

st.header("1. Upload and Process Documents")
uploaded_files = st.file_uploader(
    "Upload documents (PDF, DOCX, TXT) or Images (PNG, JPG, JPEG) for OCR",
    type=['pdf', 'docx', 'txt', 'png', 'jpg', 'jpeg'],
    accept_multiple_files=True
)

if 'processed_docs' not in st.session_state:
    st.session_state.processed_docs={}

if uploaded_files:
    with st.spinner("processing uploaded files..."):
        for uploaded_file in uploaded_files:
            if uploaded_file.name not in st.session_state.processed_docs.values():
                st.write(f"Processing {uploaded_file.name}...")
                file_path=UPLOAD_DIR / uploaded_file.name
                with open(file_path,"wb") as f:
                    f.write(uploaded_file.getbuffer())

                try:
                    text_pages=get_doc(file_path)
                    doc_id=uploaded_file.name
                    add_documnent(vector_store, doc_id, text_pages)
                    st.session_state.processed_docs[doc_id] = uploaded_file.name
                    st.success(f"processed and stored{uploaded_file.name}")
                except Exception as e:
                    st.error(f"error processing {uploaded_file.name}: {e}")
            else:
                st.info(f"{uploaded_file.name}already been processed.")

if st.session_state.processed_docs:
    st.header("2. Query Your Documents")
    st.write("available documents for querying: ",list(st.session_state.processed_docs.values()))

query = st.text_input("enter your query:", key="query_input")

if query and st.session_state.processed_docs:
    st.subheader("Individual Document Responses:")
    for doc_id, doc_name in st.session_state.processed_docs.items():
        with st.expander(f"Querying: {doc_name}"):
            try:
                answer, citations=query_document(vector_store, doc_id, query, NEBIUS_API_KEY)
                st.markdown(f"**Answer:** {answer}")
                if citations:
                    st.markdown("**Citations:**")
                    for cit in citations:
                        st.markdown(f"- Page: {cit.get('page', 'N/A')},Snippet: {cit.get('snippet', 'N/A')}")
                else:
                    st.write("no citation found")
            except Exception as e:
                st.error(f"Error querying {doc_name}: {e}")
    
    st.subheader("theme analysis")
    if st.button("analyze across all doc"):
        with st.spinner("analyzing themes..."):
            try:
                doc_ids_list=list(st.session_state.processed_docs.keys())
                theme_analysis_result = analyze_themes(vector_store, doc_ids_list, query, NEBIUS_API_KEY)
                st.markdown("**theme result**")
                st.markdown(theme_analysis_result)
            except Exception as e:
                st.error(f"error during theme{e}")
elif query and not st.session_state.processed_docs:
    st.warning("please upload doc first")

st.sidebar.info("1. Upload docs. 2. Wait for processing. 3. Ask questions.")



