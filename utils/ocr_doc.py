from PIL import Image
import pytesseract 
import fitz
from pathlib import Path
from docx import Document

def get_doc(file_path:Path) ->list:
    pages_content=[]
    ext=file_path.suffix.lower() 

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

    elif ext == ".txt": # for text file
        with open(file_path,"r",encpding="utf-8")as f:
            pages_content.append({"pages":1,"content":f.read()}) #in one pages
    
    elif ext in [".png","jpeg","jpg"]: # for images 
        try:
            text=pytesseract.image_to_string(Image.open(file_path)) # using tesseract for ocr
            pages_content.append({"page":1,"content":text})
        except Exception as e:
            print(f"ocr error for {file_path}")

    else:
        raise ValueError(f"sorry unsupported file:{ext}")
    return pages_content