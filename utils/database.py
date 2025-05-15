from langchain.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.embeddings.base import Embeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter 


def init_vector_store(persist_path:str,api_key:str):
    embeddings_model=OpenAIEmbeddings(open_api_key=api_key)
    return Chroma(persist_directory=persist_path,embedding_function=embeddings_model)

def add_documnent(vector_store:Chroma,doc_id:str,text_pages:list):
    text_splitter=RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=200)
    all_chunks = []
    for page_item in text_pages:
        page_num=page_item["page"]
        page_content=page_item["content"]
        chunks=text_splitter.split_text(page_content)
        for i, chunk_text in enumerate(chunks)
            metadata={"source":doc_id,"page":page_num,"chunk_in_page":i}
            all_chunks.append(LangchainDocument(page_content=chunk_text,metadata=metadata))
    
    if all_chunks:
        vector_store.add_documents(all_chunks)
        vector_store.persist() #changes  saved

    