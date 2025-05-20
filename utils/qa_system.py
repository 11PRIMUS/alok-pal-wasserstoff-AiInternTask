from langchain.chains import RetrievalQA
from langchain.chains.summarize import load_summarize_chain
import os
import streamlit as st
from .nebius_llm import NebiusChatModel



os.environ["LANGCHAIN_TRACING_V2"]="true"
langchain_api_key_from_env =os.getenv("LANGCHAIN_API_KEY")
if langchain_api_key_from_env:
    os.environ["LANGCHAIN_API_KEY"]=langchain_api_key_from_env
else:
    if 'st' in globals() and hasattr(st, 'sidebar') and hasattr(st.sidebar, 'warning'):
        st.sidebar.warning("Langchain api key not found , tracing disabled")
    else:
        print("Warning: Langchain API key not found, tracing disabled.")

def query_document(vector_store,doc_id:str,query:str,api_key:str):
    llm=NebiusChatModel(
        nebius_api_key=api_key, # Pass the api_key here
        model_name="meta-llama/Llama-3.3-70B-Instruct",
        temperature=0
    )
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
                "snippet":doc_source.page_content[:150]+"..." #example snippet
            })
    return answer,citations

def analyze_themes(vector_store,doc_ids:list,query:str,api_key:str):
    llm=NebiusChatModel(
        nebius_api_key=api_key, # Pass the api_key here
        model_name="meta-llama/Llama-3.3-70B-Instruct",
        temperature=0.2
    )

    all_relevant_docs_for_query=[]
    for doc_id_item in doc_ids: 
        retriever=vector_store.as_retriever(search_kwargs={"k":2,"filter":{"source":doc_id_item}})
        docs=retriever.get_relevant_documents(query)
        all_relevant_docs_for_query.extend(docs)

    if not all_relevant_docs_for_query:
        return "no relevant information found"
    combined_context ="\n\n--\n\n".join([doc.page_content for doc in all_relevant_docs_for_query])
    if len(combined_context)>12000: 
        combined_context=combined_context[:12000]+"\n..(tr)"

    prompt_template=f"""
    Analyze the text excerpts from multiple documents in relation to query:"{query}" identify common themes, variations in response and provide synthesized overview.
    Excerpts:
    {combined_context}
    Analysis:
    """ 

    response=llm.invoke(prompt_template)
    return response.content

