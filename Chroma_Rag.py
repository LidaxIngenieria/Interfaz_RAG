from abc import ABC, abstractmethod
from typing import List, Any
from file_readers import smart_doc_processing, expand_directories
from ConversationMemory import ConversationMemory
import hashlib


class Chroma_Rag(ABC):
    """
    Implementación de RAG (Retrieval-Augmented Generation) usando ChromaDB como base de datos vectorial.

    Params:
        embedding_model (str): Nombre/ruta del modelo de embeddings a usar
        llm (str): Nombre/ruta del modelo de lenguaje a usar
        vector_store (Any): Instancia de ChromaDB vector store
        text_splitter (Any): Divisor de texto para procesamiento de documentos
        reranker (Any, optional): Modelo de reranking para reordenar documentos. Por defecto None.
        k (int, optional): Número de documentos a recuperar. Por defecto 5.

    """
    

    def __init__(self, 
                embedding_model: str, 
                llm: str, 
                vector_store: Any, 
                text_splitter: Any, 
                reranker: Any= None,
                k: int= 5):
        
        self.embedding_model = embedding_model
        self.llm = llm
        self.vector_store = vector_store
        self.text_splitter = text_splitter
        self.reranker = reranker
        self.k = k

        self.conversation_memory = ConversationMemory()

    def is_file_in_store(self, file_path: str)-> bool:
        """
        Funcion ayudante para ver si un archivo ya existe en el vdb

        Params:
            vector_database(Chroma)
            file_path(str)
            
        Return bool
        """
        try:
            file_hash = hashlib.md5(file_path.encode()).hexdigest()[:8]
            existing_docs = self.vector_store.get(where={"file_hash": file_hash})
                
            return existing_docs and len(existing_docs.get('documents', [])) > 0
            
        except Exception as e:
            print(f"\nError checking file in store: {e}")
            return False         
        
    
    def add_documents(self,file_paths: List[str])-> str:
        """
        Añade documentos a la base de datos vectorial después de procesarlos en chunks y generar sus embeddings.

        Params:
            file_paths (List[str]): Lista de rutas de archivos a añadir a la base de datos vectorial
            
        """

        try:

            i = 1
            expanded_paths = expand_directories(file_paths)
            n_files = len(expanded_paths)

            print(f"Uploading files ({n_files})...")

            for path in expanded_paths:
                if self.is_file_in_store(path):
                    print(f"\n{path} already on vdb moving to next file")
                    continue

                documents, ids = smart_doc_processing(self.text_splitter,path)

                if documents is None or ids is None:
                    continue
                    
                embeddings = []
                for doc in documents:
                    content = doc.get("content")
                    embedding = self.get_embeddings(content)
                    embeddings.append(embedding)
            
                metadatas = []
                for doc in documents:
                    metadata = doc.get("metadata")
                    metadatas.append(metadata)
                
                self.vector_store.add(
                    documents=[doc["content"] for doc in documents],
                    embeddings=embeddings,
                    metadatas=metadatas,
                    ids=ids
                )
            
                print(f"\n{path} uploaded succesfully ({i}/{n_files}).")
                i += 1

            return("\nAll files succesfully uploaded")
    
        except Exception as e:
            return(f"\nError occurred when uploading files: {e}")
        
        
    def delete_documents(self, file_paths: List[str]) -> str:
        """
        Elimina documentos de la base de datos vectorial basándose en sus rutas de archivo.

        Params:
            file_paths (List[str]): Lista de rutas de archivos a eliminar de la base de datos vectorial
            
        """

        try:

            i = 1
            expanded_paths = expand_directories(file_paths)
            n_files = len(expanded_paths)

            print(f"Deleting files ({n_files})...")

            for path in expanded_paths:
                if not self.is_file_in_store(path):
                    print(f"\n{path} not on vdb moving to next file")
                    continue
                file_hash = hashlib.md5(path.encode()).hexdigest()[:8]
                self.vector_store.delete(where={"file_hash": file_hash})
                print(f"\nFile {path} deleted successfully ({i}/{n_files})")
                i += 1

            return f"\nAll files deleted successfully."
        
        except Exception as e:
            return f"\nError deleting files: {e}"
    
    
    def update_documents(self, file_paths: List[str]) -> str:
        """
        Actualiza documentos existentes en la base de datos vectorial.

        Params:
            file_paths (List[str]): Lista de rutas de archivos a actualizar en la base de datos vectorial
            
        """

        try:

            i = 1
            expanded_paths = expand_directories(file_paths)
            n_files = len(expanded_paths)

            print(f"Updating files ({n_files})...")

            for path in expanded_paths:
                if not self.is_file_in_store(path):
                    print(f"\n{path} not on vdb moving to next file")
                    continue

                documents, ids = smart_doc_processing(self.text_splitter,path)

                if documents is None or ids is None:
                    continue
                    
                embeddings = []
                for doc in documents:
                    content = doc.get("content")
                    embedding = self.get_embeddings(content)
                    embeddings.append(embedding)
            
                metadatas = []
                for doc in documents:
                    metadata = doc.get("metadata")
                    metadatas.append(metadata)
                
                self.vector_store.update(
                    documents=[doc["content"] for doc in documents],
                    embeddings=embeddings,
                    metadatas=metadatas,
                    ids=ids
                )
            
                print(f"\n{path} updated succesfully ({i}/{n_files}).")
                i += 1

            return("\nAll files succesfully updated")
    
        except Exception as e:
            return(f"\nError occurred when updating files: {e}")

        
    def retrieve(self,query: str):
        """
        Recupera documentos relevantes de la base de datos vectorial.

        Params:
            query (str): Consulta de búsqueda para recuperar documentos relevantes
            
        """
        
        results = self.vector_store.query(
            query_embeddings=self.get_embeddings(query),
            n_results= self.k,
        )

        return results
        #documents = results['documents'][0]
        #return documents
    
    
    def rerank_documents(self, query: str, init_docs: List[str], init_metadatas: List[dict]) -> List[str]:
        """
        Reordena documentos recuperados usando el modelo de reranking para mejorar la relevancia.

        Params:
            query (str): Consulta original de búsqueda
            documents (List[str]): Lista de documentos a reordenar
            
        """

        pairs = [[query, doc] for doc in init_docs]
        
        scores = self.reranker.predict(pairs)

        scored_docs = list(zip(init_docs, init_metadatas, scores))
        scored_docs.sort(key=lambda x: x[2], reverse=True)

        reranked_documents = [doc for doc, metadata, score in scored_docs]
        reranked_metadatas = [metadata for doc, metadata, score in scored_docs]

        return reranked_documents, reranked_metadatas
    

    @abstractmethod
    def invoke(self, query: str) -> None:
        """
        Método abstracto para ejecutar la consulta RAG completa.
        
        Params:
            query (str): Consulta del usuario a procesar
        """
        pass
    
    @abstractmethod
    def get_embeddings(self, text: str) -> List[float]:
        """
        Método abstracto para generar embeddings de texto.
        
        Params:
            text (str): Texto para generar embeddings
        """
        pass

    @abstractmethod
    def invoke_rerank(self, query: str) -> None:
        """
        Método abstracto para ejecutar la consulta RAG con reranking.
        
        Params:
            query (str): Consulta del usuario a procesar con reranking
        """
        pass
