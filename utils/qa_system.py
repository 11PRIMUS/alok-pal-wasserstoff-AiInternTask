from langchain.chains import RetrievalAQ
from langchain.chains.summarize import load_summarize_chain
from langchain_openai import ChatOpenAI

def query_document(vector_store,doc_id:str,query:str,api_key:str):
    llm=ChatOpenAI(model_name="gpt-3.5",temperature=0,openai_api_key=api_key)
    #retriever=get_retriever_for_doc(vector_store,doc_id)
    retriever=vector_store.as_retriever(search_kwargs={"k":3,"filter":{"source":doc_id}})
    qa_chain=RetrievalAQ.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
    )
    result=qa_chain({"query":query})
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
    llm=ChatOpenAI(model_name="gpt-3.5",temperature=0.2,openai_api_key=api_key)

    #retriever=get_retriever_for_all_docs(vector_store,doc_ids)
    all_relevant_docs_for_query=[]
    for doc_id in doc_ids:
        retriever=vector_store.as_retriever(search_kwargs={"k":2,"filter":{"source":doc_id}})
        docs=retriever.get_relevant_documents(query)
        all_relevant_docs_for_query.extend(docs)

    if not all_relevant_docs_for_query:
        return "no relevant information found"
    
    chain=load_summarize_chain(llm,chain_type="map_reduce")
    query_with_instruction=f"based on the following documnets,what are the common themes and key responses related to the query:'{query}'?"
    result=chain({"input_documents":all_relevant_docs_for_query,"question":query_with_instruction})

    response=llm.invoke(prompt)
    return response.content

