from langchain.chains import RetrievalAQ
from langchain.chains.summarize import load_summarize_chain
from langchain_openai import ChatOpenAI

def query_document(vector_store,doc_id:str,query:str,api_key:str):
    llm=ChatOpenAI(model_name="gpt-3.5",temperature=0,openai_api_key=api_key)
    
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

