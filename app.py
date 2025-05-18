import streamlit as st
from dotenv import load_dotenv
import os
from pathlib import Path
from utils.ocr_doc import get_doc
from utils.database import init_vector_store,add_documnent,get_retriever_for_all_doc,get_all_doc_ids
from utils.qa_system import query_document,analyze_themes

load_dotenv()
OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    st.error("api key not found")
    st.stop()

UPLOAD_DIR=Path("uploaded_docs")
UPLOAD_DIR.mkdir(exist_ok=True)
VECTOR_STORE_PATH="./vector_store_db"

vector_store=init_vector_store(VECTOR_STORE_PATH,OPENAI_API_KEY)
st.title("Doc_query and analysis")

st.header("upload and process documents") 
uploaded_files=st.file_uploader(
    "uploaded documents(PDF, DOCX, TXT) or Images (PNG, JPG, JPEG) for OCR",
    type=['pdf','docx','txt','png','jpg','jpeg'],
    accept_multiple_files=True
)  
if 'processed_docs' not in st.session_state:
    st.session_state.processed_docs={}

if uploaded_files:
    for uploaded_file in uploaded_files:
        if uploaded_files.name not in st.session_state.processed_docs_values():
            st.write(f"Processing{uploaded_file.name}...")
            file_path=UPLOAD_DIR/uploaded_file.name
            with open(file_path,"wb") as f:
                f.write(uploaded_file.getbuffer())

            try:
                #processing
                text_pages=get_doc(file_path)
                doc_id=uploaded_file.name
                add_documnent(vector_store,doc_id,text_pages)
                st.session_state.processed_docs[doc_id]=uploaded_file.name
                st.success(f"processed and stored: {uploaded_file.name}")
            except Exception as e:
                st.error(f"error processing {uploaded_file.name}: {e}")
        
        else:
            st.info(f"{uploaded_file.name} already processed")

if st.session_state.processed_docs:
    st.header("2. Processed docs")
    doc_ids=get_all_doc_ids(vector_store)
    selected_doc_id_for_query=st.selectbox("Select doc for individual query:", options=list(st.session_state.processed_docs.keys()),format_func=lambda x:st.session_state.processed_docs[x])

    st.write("available doc for querying: ",list(st.session_state.processed_docs.values()))

