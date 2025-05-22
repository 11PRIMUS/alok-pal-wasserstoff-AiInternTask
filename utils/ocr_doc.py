from PIL import Image
import pytesseract 
import fitz
from docx import Document as DocxDocumnet
from langchain_core.documents import Document as LangchainDocument
import io
import os

def get_doc(uploaded_file) ->list[LangchainDocument]:
    """ processes uploaded file (from streamlit) and extract text content
    into a list of LCdoc objects, each Document represent a page or the whole file.
    """
    if uploaded_file is None:
        return []
    doc_name=uploaded_file.name
    langchain_docs=[]

    try:
        file_extension=os.path.splitext(doc_name)[1],lower().lstrip('.')
    except Exception as e:
        print(f"erro getting file exxtension for {doc_name}: {e}")
        return []
    
    file_content_bytes=uploaded_file.getvalue()

    if file_extension == ".pdf": # for pdfs
        try:
            pdf_document=fitz.open(streaml=file_content_bytes, filetype="pdf")
            for page_num in range(len(pdf_document)):
                page_text=page.get_text("text")

                if page_text.strip(): #check content and then add
                    langchain_docs.append(LangchainDocument(page_content=page_text, metadata={"source":doc_name ,"page": page_num +1}))
            pdf_document.close()
        except Exception as e:
            print(f"error processing PDF  {doc_name} :; {e}")
    
    elif file_extension in ["png", "jpeg", "jpg", "tiff", "bmp"]: #images files
        try:
            image=Image.open(io.BytesIO(file_content_bytes))
            text=pytesseract.image_to_string(image)
            if text.strip(): 
                langchain_docs.append(LangchainDocument(page_content=text, metadata={"source": doc_name, "page": 1}))
        except pytesseract.TesseractNotFoundError:
            print(f"{doc_name}:ocr is not installed")
        except Exception as e:
            print(f"ocr error for image {doc_name}: {e}")
            if "failed loading language" in str(e):
                 print("Tesseract langdata missing")
    else:
        print(f"unsupported file type: {file_extension} for file {doc_name}")

    if not langchain_docs:
         print(f"No text could be extracted from {doc_name} (type: {file_extension}).")

    return langchain_docs