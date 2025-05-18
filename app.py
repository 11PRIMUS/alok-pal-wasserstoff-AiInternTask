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
        if uploaded_file.name not in st.session_state.processed_docs.values():
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

st.header("Ask questions")
query=st.text_input("enter your query:")

if query and st.session_state.processed_docs:
    st.subheader("individual doc response:")
    for doc_id,doc_name in st.session_state.processed_docs.items():
        st.write(f"**querying: {doc_name}**")
        try:
            response,citations=query_document(vector_store, doc_id,query,OPENAI_API_KEY)
            st.markdown(f"**answer:** {response}")
            if citations:
                st.markdown("**citations:**")
                for cit in citations:
                    st.markdown(f"- Page:{cit.get('page','N/A')}, Snippet: {cit.get('snippet','N/A')}") 
            else:
                st.write("no specific citations found, or answer is general.")
        except Exception as e:
            st.error(f"error querying {doc_name}: {e}")
        st.markdown("---")
    
    st.subheader("cross_doc theme analysis:")
    if st.button("analyze theme across all docs"):
        try:
            theme_analysis=analyze_themes(vector_store, list(st.session_state.processed_docs.keys()), query, OPENAI_API_KEY)
            st.markdown(theme_analysis)
        except Exception as e:
            st.error(f"error in theme analysis:{e}")
    else:
        if not st.session_state.processed_docs:
            st.warning("please upload and process doc first")
    st.sidebar.info("upload docs, then ask question ")



