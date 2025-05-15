from PIL import Image
import pytesseract 
import fitz
from pathlib import Path

def get_doc(file_path:Path) ->list:
    pages_count=[]
    ext=file_path.suufix.lower()

    if ext == ".pdf": # for pdfs
        doc=fitz.open(file_path)
        for page_num, page in enumerate(doc):
            pages_content.append({"page":page_num+1,"content":page.get_text()})
            doc.close()
    
    elif ext==".docx": #for docx files 
        doc=Document(file_path)
        full_text=[]
        for para in doc.paragraphs:
            full_text.append(para.text)
        pages_content.append({"page":1,"content":"\n".join(full_text)})