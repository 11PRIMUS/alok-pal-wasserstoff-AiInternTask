from langchain.chains import RetrievalQA
from langchain.chains.summarize import load_summarize_chain
import os
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document as LangchainDocument



os.environ["LANGCHAIN_TRACING_V2"]="true"
langchain_api_key =st.secrets.get("LANGCHAIN_API_KEY")
if langchain_api_key:
    os.environ["LANGCHAIN_API_KEY"]=langchain_api_key
else:
    try:
        if st.sidebar: #checks for streamlit sidebar
            st.sidebar.warning("Langchain api key missing. langsmith tracing disabled")
    except AttributeError:
        print("Warning: Langchain api key not found and tracing disabled")

def _get_llm():
    """helper func to init nebius"""
    nebius_api_key=st.secrets.get("NEBIUS_API_KEY")
    nebius_base_url="https://api.studio.nebius.com/v1/"
    nebius_model_name="meta-llama/Llama-3.3-70B-Instruct"

    if not all([nebius_api_key,nebius_base_url,nebius_model_name]):
        error_msg="nebius api key missing"
        try:
            if st.error:st.error(error_msg)
        except AttributeError:
            print(f"erro: {error_msg}")
        raise ValueError(error_msg)
    
    return ChatOpenAI(
        model=nebius_model_name,
        api_key=nebius_api_key,
        base_url=nebius_base_url,
        temperature=0
    )

def query_document(vector_store, doc_id:str,query:str):
    """queries a specific document using nebius"""
    llm=_get_llm()
    llm.temperature=0.0

    #retriever=get_retriever_for_doc(vector_store,doc_id)
    retriever=vector_store.as_retriever(search_kwargs={"k":3,"filter":{"source":doc_id}})
    qa_chain=RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
    )
    result=qa_chain.invoke({"query":query}) 
    answer=result["result"]
    citations=[]
    if result.get("source_documents"):
        for doc_source in result["source_documents"]:
            citations.append({
                "page":doc_source.metadata.get("page","N/A"),
                "snippet":doc_source.page_content[:200]+"..." #example snippet
            })
    return answer,citations

def analyze_themes(vector_store, doc_ids:list, query:str):
    llm=_get_llm()
    llm.temperature=0.2 #for summarization

    docs_for_summarization=[]

    if not doc_ids:
        return "no documents selected for theme analysis"

    all_relevant_chunks=[]
    for doc_id_item in doc_ids: 
        retriever=vector_store.as_retriever(search_kwargs={"k":3, "filter":{"source":doc_id_item}}) #k top chunks
        relevant_chunks_for_doc=retriever.invoke(query)
        all_relevant_chunks.extend(relevant_chunks_for_doc)

    docs_for_summarization=[LangchainDocument(page_content=chunk.page_content, metadata=chunk.metadat) for chunk in all_relevant_chunks]


    if not docs_for_summarization:
        return "no relevant information found"
    
    #summarization chain
    try:
        #question params in summarization_chain helos guide the summary
        chain=load_summarize_chain(llm, chain_type="map_reduce")
        summary_result=chain.invoke({"input_documnets": docs_for_summarization, "question": f"summarize them related to :{query}"})
        return summary_result["ouput_text"]
    
    except Exception as e:
        return f"{e} try a more specific theme or fewer documents"
    
