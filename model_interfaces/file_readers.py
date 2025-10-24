
import os
import hashlib
import glob
import pymupdf4llm

from langchain_text_splitters import MarkdownTextSplitter
from typing import Any, List
from PyPDF2 import PdfReader
from docx import Document 



def read_pdf(file_path: str) -> str:
    """
    Lee y extrae texto de archivos PDF.

    Params:
        file_path (str): Ruta al archivo PDF

    """
    text = ""
    with open(file_path, 'rb') as file:
        reader = PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text

#Rendundante
def read_docx(file_path: str) -> str:
    """
    Lee y extrae texto de archivos DOCX y DOC.

    Params:
        file_path (str): Ruta al archivo DOCX/DOC

    """
    doc = Document(file_path)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

#Rendundante
def read_txt(file_path: str ) -> str:
    """
    Lee y extrae texto de archivos de texto plano (TXT, MD, RTF).

    Params:
        file_path (str): Ruta al archivo de texto

    """
    
    text = ""
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    return text


def expand_directories(file_paths: List[str]) -> List[str]:
    """
    Expande directorios en una lista de archivos soportados y filtra por extensiones válidas.

    Params:
        file_paths (List[str]): Lista de rutas que pueden incluir archivos y directorios

    """
    supported_extensions = ['.txt', '.pdf', '.docx', '.doc', '.md', '.rtf']
    expanded_paths = []
    
    for path in file_paths:
        if os.path.isdir(path):
            for ext in supported_extensions:
                pattern = os.path.join(path, f"*{ext}")
                expanded_paths.extend(glob.glob(pattern))
                pattern_upper = os.path.join(path, f"*{ext.upper()}")
                expanded_paths.extend(glob.glob(pattern_upper))

        elif os.path.isfile(path):
            file_ext = os.path.splitext(path)[1].lower()
            if file_ext in supported_extensions:
                expanded_paths.append(path)
            else:
                print(f"Skipping unsupported file type: {path}")
        else:
            print(f"Path not found: {path}")
    
    
    expanded_paths = sorted(list(set(expanded_paths)))
    return expanded_paths


def smart_doc_processing(text_splitter: Any, file_path: str) -> str:
    """
    Función ayudante para preparar chunks de un archivo (PDF, DOCX, DOC, TXT, MD, RTF) 
    para la base de datos de Chroma.

    Params:
        text_splitter (TextSplitter): Divisor de texto para crear chunks
        file_path (str): Ruta al archivo a procesar

    """
    chunks = []

    try:

        #Alomejor cambiar para usar una clase unifica para tokenizador en vez usar if statements pero por ahora sirve

        if text_splitter is MarkdownTextSplitter:
  
            document= pymupdf4llm.to_markdown(file_path,write_images= True, image_path= "images")

            raw_chunks = text_splitter.create_documents([document])

            for raw_chunk in raw_chunks:
                chunks.append(raw_chunk.page_content)

        else: 

            file_ext = os.path.splitext(file_path)[1].lower()

            if file_ext == '.pdf':
                document = read_pdf(file_path)
            #Remover despues
            elif file_ext in ['.docx', '.doc']:
                document = read_docx(file_path)
            elif file_ext in ['.txt', '.md', '.rtf']:
                document = read_txt(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_ext}")

            chunks = text_splitter.chunks(document)

        file_hash = hashlib.md5(file_path.encode()).hexdigest()[:8] # Hash identificador para cada documento

        documents = []
        ids = []
        for i, chunk in enumerate(chunks, 1):
            document = {
                "content": chunk,
                "metadata": {
                    "source": file_path,
                    "file_hash": file_hash,
                    "chunk_id": i
                }
            }

            documents.append(document)
            ids.append(f"{file_hash}_{i}")

        return documents, ids

    except Exception as e:
        print(f"Error creating chunks for file: {e}")
        return None, None
    
    

# def main():

#     file_path = "lidax_pdf/08 - INT_LDX_ISD_TEC_009__2-1_Diseño de Taladros.pdf"

#     from langchain_text_splitters import MarkdownTextSplitter
#     markdownsplitter = MarkdownTextSplitter()

#     docs , ids = smart_doc_for_markdown(markdownsplitter,  file_path)

#     for doc in docs:
#         print(f"\n\n{doc}")


# if __name__ == "__main__":
#     main()