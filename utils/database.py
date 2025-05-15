from langchain.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.embeddings.base import Embeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter 
from langchain.docstore.document import Document as LangchainDocument


#chroma vector using openai embedding model
def init_vector_store(persist_path:str,api_key:str):
    embeddings_model=OpenAIEmbeddings(open_api_key=api_key)
    return Chroma(persist_directory=persist_path,embedding_function=embeddings_model)

def add_documnent(vector_store:Chroma,doc_id:str,text_pages:list):
    text_splitter=RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200) # add doc to vector_dtore
    all_chunks = []
    for page_item in text_pages:
        page_num=page_item["page"]
        page_content=page_item["content"]
        chunks=text_splitter.split_text(page_content)
        for i, chunk_text in enumerate(chunks):
            metadata={"source":doc_id,"page":page_num,"chunk_in_page":i} #index of chunk
            all_chunks.append(LangchainDocument(page_content=chunk_text,metadata=metadata))
    
    if all_chunks:
        vector_store.add_documents(all_chunks)
        vector_store.persist() #changes  saved

 #search interface for one doc   
def get_retriever_for_doc(vector_store:Chroma,doc_id:str,k_results=3):
    return vector_store.as_retriever(search_kwargs={"k":k_results,"filter":{"source":doc_id}})

def get_retriever_for_all_doc(vector_store:Chroma,k_results=5): #retereiver across all doc in vector_store
    return vector_store.as_retriver(search_kwargs={"k":k_results})

#extract ids from vectordb
def get_all_doc_ids(vector_store:Chroma)-> list:
    try:
        #if chroma works fine that good otherwise i am going with Qdrant 
        results=vector_store.get(include=["metadatas"])
        if results and results['metadatas']:
            return list(set(meta['source'] for meta in results['metadatas'] if 'source' in meta))
    except Exception as e:
        print(f"error getting all doc ids:{e}")
    return []

    