import streamlit as st
from dotenv import load_dotenv
import os
from utils.ocr_doc import get_doc
from utils.database import init_vector_store, add_document, get_all_doc_ids
from utils.qa_system import query_document, analyze_themes

load_dotenv()

VECTOR_STORE_PATH="./vector_store_db"

if not os.getenv("NEBIUS_API_KEY"):
    st.error("check nebius config")
    st.stop()
try:
    vector_store=init_vector_store(VECTOR_STORE_PATH)
    st.sidebar.success("vector store intialized ")
except Exception as e:
    st.error(f"failed to init vector store{e}")
    st.stop()
    
#sessions tart

if "processed_documents" not in st.session_state:
    #show existing doc when no new docs
    try:
        st.session_state.processed_documents=set(get_all_doc_ids(vector_store))
        if st.session_state.processed_documents:
            st.sidebar.info(f"loaded {len(st.session_state.processed_documents)} existing docs from vs.")
    except Exception as e:
        st.sidebar.warning(f"can't preload docs {e}")
        st.session_state.processed_documents = set()

if "document_contents" not in st.session_state: 
    st.session_state.document_contents={}
st.title("Document Query and Analysis ")

#sidebar
st.sidebar.header("Doc Manager")
uploaded_files =st.sidebar.file_uploader("upload documents (PDF, DOCX, TXT, Images)", type=["pdf", "docx", "txt", "png", "jpg", "jpeg"], accept_multiple_files=True)

if uploaded_files:
    for uploaded_file in uploaded_files:
        doc_name=uploaded_file.name
        if doc_name not in st.session_state.processed_documents:
            with st.spinner(f"processing {doc_name}..."):
                try:
                    docs=get_doc(uploaded_file) 
                    if docs:
                        add_document(vector_store, docs) #liist doc
                        st.session_state.processed_documents.add(doc_name)
                        st.session_state.document_contents[doc_name]=f"processed on {pd.Timestamp.now()}"
                        st.success(f"processed {doc_name}")
                    else:
                        st.error(f"failed to extract text{doc_name}")
                except Exception as e:
                    st.error(f"error processing {doc_name}: {e}")
        else:
            st.sidebar.info(f"{doc_name} already processed.")
    available_documents=list(st.session_state.processed_documents)

#available_doc
available_documents = sorted(list(st.session_state.processed_documents))


#Q&A
tab1, tab2=st.tabs(["ask document ", "analyze theme"])

with tab1:
    st.header("Query a Specific Document")
    if not available_documents:
        st.info("upload and process doc ")
    else:
        selected_doc_for_query=st.selectbox("select a document to query", available_documents, key="query_doc_select", index=0 if available_documents else None)
        if selected_doc_for_query:
            query=st.text_input(f"ask a question about {selected_doc_for_query}", key="doc_query_input")
            if st.button("Get Answer", key="get_doc_answer_btn"):
                if query:
                    with st.spinner("searching for answer..."):
                        try:
                            answer, citations=query_document(
                                vector_store=vector_store,
                                doc_id=selected_doc_for_query,
                                query=query
                            )
                            st.markdown("### Answer")
                            st.markdown(answer)
                            if citations:
                                st.markdown("### Citations")
                                for i, citation in enumerate(citations):
                                    st.markdown(f"**Citation {i+1}:** (Page {citation.get('page','N/A')})")
                                    st.caption(f"Snippet: {citation.get('snippet','no snippet available.')}")
                        except Exception as e:
                            st.error(f"error querying document: {e}")
                else:
                    st.warning("enter a question.")

with tab2:
    st.header("Analyze Themes Across Documents")
    if not available_documents:
        st.info("upload and process one doc atleast")
    else:
        selected_docs_for_theme=st.multiselect("select documents for theme analysis", available_documents, key="theme_docs_select", default=available_documents if len(available_documents) <=3 else [])
        theme_query=st.text_input("what themes are you interested in! (e.g., 'performance', 'key challenges')", key="theme_query_input")

        if st.button("analyze themes", key="analyze_themes_btn"):
            if selected_docs_for_theme and theme_query:
                with st.spinner("analyzing themes..."):
                    try:
                        themes_output=analyze_themes(
                            vector_store=vector_store,
                            doc_ids=selected_docs_for_theme,
                            query=theme_query
                        )
                        st.markdown("### Identified Themes")
                        st.markdown(themes_output)
                    except Exception as e:
                        st.error(f"error analyzing themes: {e}")
            elif not selected_docs_for_theme:
                st.warning("select at least one doc for theme analysis.")
            else: # theme_query is empty
                st.warning("specify the theme criteria.")

