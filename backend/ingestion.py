import PyPDF2
import re
from typing import List, Dict
from langchain.text_splitter import RecursiveCharacterTextSplitter, SentenceTransformersTokenTextSplitter

def process_pdf_fixed_size(file_path: str, chunk_size: int = 500, chunk_overlap: int = 50) -> List[Dict]:
    chunks = []
    
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        
        for page_num, page in enumerate(reader.pages):
            text = page.extract_text()
            
            # Simple chunking by character count
            for i in range(0, len(text), chunk_size - chunk_overlap):
                chunk_text = text[i:i+chunk_size]
                chunks.append({
                    "text": chunk_text,
                    "page": page_num + 1,
                    "start_index": i
                })
    
    return chunks

def process_pdf_sentence_aware(file_path: str, chunk_size: int = 500, chunk_overlap: int = 50) -> List[Dict]:
    chunks = []
    
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        
        for page_num, page in enumerate(reader.pages):
            text = page.extract_text()
            
            # Split into sentences
            sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s', text)
            
            current_chunk = ""
            for sentence in sentences:
                if len(current_chunk) + len(sentence) > chunk_size:
                    if current_chunk:
                        chunks.append({
                            "text": current_chunk,
                            "page": page_num + 1,
                            "start_index": text.find(current_chunk)
                        })
                    current_chunk = sentence
                else:
                    if current_chunk:
                        current_chunk += " " + sentence
                    else:
                        current_chunk = sentence
            
            if current_chunk:
                chunks.append({
                    "text": current_chunk,
                    "page": page_num + 1,
                    "start_index": text.find(current_chunk)
                })
    
    return chunks

def process_pdf_paragraph_aware(file_path: str, chunk_size: int = 500) -> List[Dict]:
    chunks = []
    
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        
        for page_num, page in enumerate(reader.pages):
            text = page.extract_text()
            
            # Split into paragraphs
            paragraphs = text.split('\n\n')
            
            for paragraph in paragraphs:
                if paragraph.strip():
                    # If paragraph is too long, split it
                    if len(paragraph) > chunk_size:
                        for i in range(0, len(paragraph), chunk_size):
                            chunk_text = paragraph[i:i+chunk_size]
                            chunks.append({
                                "text": chunk_text,
                                "page": page_num + 1,
                                "start_index": text.find(paragraph) + i
                            })
                    else:
                        chunks.append({
                            "text": paragraph,
                            "page": page_num + 1,
                            "start_index": text.find(paragraph)
                        })
    
    return chunks

def process_pdf_recursive_character(file_path: str, chunk_size: int = 500, chunk_overlap: int = 50) -> List[Dict]:
    chunks = []
    
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        
        for page_num, page in enumerate(reader.pages):
            text = page.extract_text()
            

            splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                length_function=len,
            )
            
            page_chunks = splitter.split_text(text)
            
            for chunk_text in page_chunks:
                start_index = text.find(chunk_text)
                chunks.append({
                    "text": chunk_text,
                    "page": page_num + 1,
                    "start_index": start_index if start_index >= 0 else 0
                })
    
    return chunks

def process_pdf(file_path: str, chunking_method: str = "fixed_size", **kwargs) -> List[Dict]:
    method_map = {
        "fixed_size": process_pdf_fixed_size,
        "sentence_aware": process_pdf_sentence_aware,
        "paragraph_aware": process_pdf_paragraph_aware,
        "recursive_character": process_pdf_recursive_character
    }
    
    if chunking_method not in method_map:
        raise ValueError(f"Unknown chunking method: {chunking_method}")
    
    return method_map[chunking_method](file_path, **kwargs)

def get_available_chunking_methods():
    from config import CHUNKING_METHODS
    return CHUNKING_METHODS