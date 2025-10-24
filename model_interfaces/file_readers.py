from PyPDF2 import PdfReader
from PIL import Image
from docx import Document 
import os
import hashlib
import glob
from typing import Any, List, Tuple, Dict
import pymupdf
import pymupdf4llm

def read_as_markdown(file_path: str) :

    try:

        md_text = pymupdf4llm.to_markdown(file_path,write_images= True, image_path= "images")

        return md_text
    
    except Exception as e:
        print(f"{e}")






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


def read_pdf_for_rag(file_path: str) -> str:
    """
    Lee y extrae el contenido de un PDF usando pymupdf4llm.

    Esta función convierte el PDF directamente a formato Markdown.

    Params:
        file_path (str): Ruta al archivo PDF

    """

    excluded_hashes = []  
    
    image_dir = "images"
    
    try:
        print(f"Extrayendo contenido a: {image_dir}")
        os.makedirs(image_dir, exist_ok=True)
        
        doc = fitz.open(file_path)
        md_lines = []
        image_counter = 0
        
        for page_num, page in enumerate(doc):
            # Texto markdown
            text = page.get_text("markdown")
            md_lines.append(text)
            
            # Procesar imágenes
            image_list = page.get_images()
            
            for img_index, img in enumerate(image_list):
                try:
                    xref = img[0]
                    pix = fitz.Pixmap(doc, xref)
                    
                    if pix.n - pix.alpha < 4:
                        img_data = pix.tobytes("png")
                        img_hash = hashlib.md5(img_data).hexdigest()
                        
                        # Verificar si está en la lista de exclusiones
                        if img_hash in excluded_hashes:
                            print(f"Skipping excluded image on page {page_num+1}")
                            continue

                        image_counter += 1
                        img_name = f"image_{image_counter}.png"
                        img_path = os.path.join(image_dir, img_name)
                        pix.save(img_path)
                        
                        md_lines.append(f"![Image {image_counter}]({img_path})")
                    
                    pix = None
                    
                except Exception as e:
                    print(f"Error processing image: {e}")
                    continue
        
        doc.close()
        return "\n\n".join(md_lines)
    
    except EmptyFileError:
        print(f"Error: El archivo '{file_path}' está vacío o dañado.")
        return ""
    
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo en '{file_path}'.")
        return ""


    
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

def smart_doc_processing(text_splitter: Any, file_path: str) -> str:
    """
    Función ayudante para preparar chunks de un archivo (PDF, DOCX, DOC, TXT, MD, RTF) 
    para la base de datos de Chroma.

    Params:
        text_splitter (TextSplitter): Divisor de texto para crear chunks
        file_path (str): Ruta al archivo a procesar

    """
    raw_document = ""

    try:
        file_ext = os.path.splitext(file_path)[1].lower()

        if file_ext == '.pdf':
            raw_document = read_pdf(file_path)
            #raw_document = read_pdf_for_rag(file_path)
        elif file_ext in ['.docx', '.doc']:
            raw_document = read_docx(file_path)
        elif file_ext in ['.txt', '.md', '.rtf']:
            raw_document = read_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")

        chunks = text_splitter.chunks(raw_document)

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
    
def smart_doc_for_markdown(markdown_splitter: Any, file_path: str) -> str:

    markdown= ""

    try:
        markdown = read_as_markdown(file_path)

        chunks = markdown_splitter.create_documents([markdown])

        file_hash = hashlib.md5(file_path.encode()).hexdigest()[:8] # Hash identificador para cada documento

        documents = []
        ids = []
        for i, chunk in enumerate(chunks, 1):
            document = {
                "content": chunk.page_content,
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


def main():

    file_path = "lidax_pdf/08 - INT_LDX_ISD_TEC_009__2-1_Diseño de Taladros.pdf"

    from langchain_text_splitters import MarkdownTextSplitter
    markdownsplitter = MarkdownTextSplitter()

    docs , ids = smart_doc_for_markdown(markdownsplitter,  file_path)

    for doc in docs:
        print(f"\n\n{doc}")


if __name__ == "__main__":
    main()