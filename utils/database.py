import os
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from typing import List

#chroma vector using sentence transformer
def init_vector_store(persist_path:str):
    embeddings_model=HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return Chroma(persist_directory=persist_path,embedding_function=embeddings_model)

def add_document(vector_store:Chroma,docs:List[Document]):
    text_splitter=RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    all_chunks = []
    for doc in docs: # docs list of LCdocs
        source=doc.metadata.get("source","Unknown Source")
        page=doc.metadata.get("page","N/A") #page info from ocr_doc

        chunks_text=text_splitter.split_text(doc.page_content) #split content of this doc
        for i,chunk_t in enumerate(chunks_text):
            #new doc object for chunk
            chunk_metadata = {"source": source, "page": page, "chunk_in_page": i}
            all_chunks.append(Document(page_content=chunk_t, metadata=chunk_metadata))
    
    if all_chunks:
        vector_store.add_documents(all_chunks)

 #search interface for one doc   
def get_retriever_for_doc(vector_store:Chroma,doc_id:str,k_results=3):
    return vector_store.as_retriever(search_kwargs={"k":k_results,"filter":{"source":doc_id}})

def get_retriever_for_all_doc(vector_store:Chroma,k_results=5): #retriever across all doc in vector_store
    return vector_store.as_retriever(search_kwargs={"k":k_results})

#extract ids from vectordb
def get_all_doc_ids(vector_store:Chroma)-> list:
    try:
        all_retrieved_docs = vector_store.get(include=["metadatas"]) 
        if all_retrieved_docs and all_retrieved_docs.get('metadatas'):
            #unique source names from metadata

            return list(set(meta['source'] for meta in all_retrieved_docs['metadatas'] if meta and 'source' in meta))
    except Exception as e:
        print(f"error getting all doc ids:{e}")
    return []
