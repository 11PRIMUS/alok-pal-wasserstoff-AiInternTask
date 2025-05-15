from PIL import Image
import pytesseract 
import fitz
from pathlib import Path

def get_doc(file_path:Path) ->list:
    pages_count=[]
    ext=file_path.suufix.lower()

    if ext == ".pdf":
        doc=fitz.open(file_path)
        for page_num, page in enumerate(doc):
            pages_content.append({"page":page_num+1,"content":page.get_text()})
            doc.close()