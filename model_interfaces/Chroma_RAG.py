import hashlib
import re

from chromadb import PersistentClient, errors
from typing import List, Any, Iterator

from model_interfaces.ConversationMemory import ConversationMemory
from model_interfaces.Text_Model import Text_Model
from model_interfaces.Embedding_Model import  Embedding_Model
from model_interfaces.Visual_Model import Visual_Model
from model_interfaces.file_readers import smart_doc_processing, expand_directories



class Chroma_RAG():
    """
    Implementación de RAG (Retrieval-Augmented Generation) usando ChromaDB como base de datos vectorial.

    Params:
        embedding_model (str): Nombre/ruta del modelo de embeddings a usar.
        llm (str): Nombre/ruta del modelo de lenguaje a usar.
        vector_store (Any): Instancia de ChromaDB vector store.
        text_splitter (Any): Divisor de texto para procesamiento de documentos.
        reranker (Any, optional): Modelo de reranking para reordenar documentos. Por defecto None.
        k (int, optional): Número de documentos a recuperar. Por defecto 5.
        top_k(int,opcional): Número de documentos que se usan después del rerank si se a proporcionado un reranker. Por defecto 3.
        print_documents(bool,opcional): Boolean por si queres que imprime los chunks que se usaron para generar la respuesta. Por defecto False.

    """
    

    def __init__(self, 
                embedding_model: Embedding_Model,
                text_splitter: Any,
                multimodal_model: Any = None, 
                text_model: Text_Model= None, 
                visual_model: Visual_Model = None,
                query_enhancer: Text_Model= None,
                reranker: Any= None,
                k: int= 5,
                top_k: int= 3,
                print_documents: bool = False,
                keep_memory: bool = False):
        
        self.embedding_model = embedding_model
        self.text_splitter = text_splitter
        self.multimodal_model = multimodal_model
        self.text_model = text_model
        self.visual_model = visual_model
        self.query_enhancer = query_enhancer
        self.reranker = reranker
        self.k = k
        self.top_k = top_k
        self.print_documents = print_documents
        self.keep_memory = keep_memory
        self.conversation_memory = None
        self.vector_store = None

        if self.keep_memory:
            self.conversation_memory = ConversationMemory()

        try:

            chroma_collection = embedding_model.model_name + "_vdb"# Si no lo encuentra lo crea automaticamente
            client_chroma = PersistentClient()
            self.vector_store= client_chroma.get_or_create_collection(chroma_collection)

        except errors.InvalidArgumentError as iae:
            tokens =embedding_model.split("/")
            chroma_collection = tokens[1] + "_vdb"
            client_chroma = PersistentClient()
            self.vector_store= client_chroma.get_or_create_collection(chroma_collection)



    def is_file_in_store(self, file_path: str)-> bool:
        """
        Funcion ayudante para ver si un archivo ya existe en el vdb

        Params:
            vector_database(Chroma)
            file_path(str)
            
        """
        try:
            file_hash = hashlib.md5(file_path.encode()).hexdigest()[:8]
            existing_docs = self.vector_store.get(where={"file_hash": file_hash})
                
            return existing_docs and len(existing_docs.get('documents', [])) > 0
            
        except Exception as e:
            print(f"\nError checking file in store: {e}")
            return False         
        
    
    def add_to_vector_store(self,file_paths: List[str])-> str:
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
                    i += 1
                    continue

                documents, ids = smart_doc_processing(self.text_splitter,path)

                if documents is None or ids is None:
                    continue
                    
                embeddings = []
                chunks = []
                for doc in documents:
                    content = doc.get("content")
                    chunks.append(content)
            
                embeddings = self.embedding_model.generate_embeddings(chunks)
            
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
        
        

        
    def delete_from_vector_store(self, file_paths: List[str]) -> str:
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
    
    
    def update_from_vector_store(self, file_paths: List[str]) -> str:
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

                chunks = []
                for doc in documents:
                    content = doc.get("content")
                    #embedding = self.get_embeddings(content)
                    chunks.append(doc)

                embeddings = self.embedding_model.geenerate_embeddings(chunks)

            
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
            query_embeddings=self.embedding_model.generate_embeddings([query]),
            n_results= self.k,
        )

        return results
        #Ver mas metodos de retrieval
    
    
    def rerank_documents(self, query: str, init_docs: List[str], init_metadatas: List[dict]) -> List[str]:
        """
        Reordena documentos recuperados usando el modelo de reranking para mejorar la relevancia.

        Params:
            query (str): Consulta original de búsqueda
            documents (List[str]): Lista de documentos a reordenar
            
        """

        pairs = [[query, doc] for doc in init_docs]

       #Alomejor hay que cambiar para otros rerankers 
        
        scores = self.reranker.predict(pairs)

        scored_docs = list(zip(init_docs, init_metadatas, scores))
        scored_docs.sort(key=lambda x: x[2], reverse=True)

        reranked_documents = [doc for doc, metadata, score in scored_docs]
        reranked_metadatas = [metadata for doc, metadata, score in scored_docs]

        return reranked_documents, reranked_metadatas
    
    

    def invoke(self, query: str, testing:bool = False):
        """
        Metodo para ejecutar la aquitectura RAG. Imprime la respuesta en consola.

        Params:
        query(str): Input de usuario

        """
        if self.keep_memory:

            self.conversation_memory.add_message("user",query)

            relevant_messages = self.conversation_memory.get_full_history()

            conversation_history = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in relevant_messages])
            
            if self.query_enhancer:
                query = self.llm.enhance_query(query, conversation_history)

        results = self.retrieve(query)
        documents = results['documents'][0]
        metadatas = results.get('metadatas', [[]])[0]

        if self.reranker:
            
            reranked_docs, reranked_metadatas = self.rerank_documents(query, documents, metadatas)
            documents = reranked_docs[:self.top_k]
            metadatas = reranked_metadatas[:self.top_k]

        retrieval_context = "\n".join([f"Document {i+1}: {doc}" for i, doc in enumerate(documents)])

        manual_prompt = f"""Task: ANSWER: Using only the provided context
        Context: {retrieval_context}

        Question: {query}

        Answer:"""

        stream = self.llm.generate_stream(manual_prompt)

        bool_print = True

        if testing:
            bool_print = False

        full_response = self.llm.get_full_response(stream, bool_print= bool_print)

        if full_response and self.keep_memory:
            self.conversation_memory.add_message("system", full_response)

        if self.print_documents:

            print("\nDocuments used:")
            for i, metadata in enumerate(metadatas):
                file_path = metadata.get('source', f"Document {i+1}")
                print(f"\nDocument {i+1}: {file_path}")


        if testing:

            sources = []

            
            for i, (metadata, doc_content) in enumerate(zip(metadatas, documents)):
                sources.append({
                "id": i + 1,
                "title": metadata.get('source', f"Document {i+1}"),
                "content": doc_content
                #"content": doc_content[:200] + "..." if len(doc_content) > 200 else doc_content
                })
        
            return{
                "answer": full_response,
                "sources": sources,  
                "query": query  
            }



    def invoke_for_frontend(self, query: str) -> Iterator[dict]:
        """
        Metodo para ejcutar codigo para el frontend deolviendo Iterators que REACT puede interpretar

        Params:
            query(str)
        """

        if self.keep_memory:

            self.conversation_memory.add_message("user", query)
            
            relevant_messages = self.conversation_memory.get_full_history()
            conversation_history = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in relevant_messages])

            query = self.query_enhancer.enhance_query(query,conversation_history)
        
        results = self.retrieve(query)
        documents = results['documents'][0]
        metadatas = results['metadatas'][0]

        if self.reranker:
            reranked_docs, reranked_metadatas = self.rerank_documents(query, documents, metadatas)
            documents = reranked_docs[:self.top_k]
            metadatas = reranked_metadatas[:self.top_k]
        
        retrieved_context = "\n".join([f"Document {i+1}: {doc}" for i, doc in enumerate(documents)])

        pattern = r'!\s*\[\]\s*\((images/[^)]+\.png)\)'
        image_references = re.findall(pattern, retrieved_context)
        
        if image_references:
            yield {"type": "images", "content": image_references}

            if self.visual_model:
                captions = self.image_model.image_to_text(image_references, query)


        SYSTEM_PROMPT_GPT = f"""

            You are an expert Q&A assistant. Your task is to answer the user's question ONLY using the provided context.
            If the answer cannot be found in the context, you must state that the information is not available in the provided documents.

            --- CONTEXT ---
            {retrieved_context}
            --- END CONTEXT ---

            Please answer the following question:
            {query}
        """

        SYSTEM_PROMPT_MISTRAL = f"""
        <s>[INST]
        You are a helpful, accurate, and concise question-answering assistant.
        Your task is to answer the user's question ONLY based on the context provided below.
        If the context does not contain the answer, state clearly, "I cannot find the answer in the provided documents."

        --- CONTEXT ---
        {retrieved_context}
        --- END CONTEXT ---

        Question: {query}

        Answer:
        [/INST]
        """


        llm_stream = self.text_model.generate_stream(SYSTEM_PROMPT_MISTRAL) 


        full_response = ""
        for chunk in llm_stream:

            chunk_text = chunk.get('response', '') 
            

            yield {"type": "chunk", "content": chunk_text}

            full_response += chunk_text


        if full_response and self.keep_memory:
            self.conversation_memory.add_message("system", full_response)

        if self.print_documents:

            print("\nDocument used:\n")

            for i, doc in enumerate(documents):
                print(f"\nDOCUMENT {i+1}:")
                print(f"\n{doc}\n\n{"-"*100}")


        def _format_sources( documents: list, metadatas: list) -> list:
            """
            Funcion ayudante para formetear las fuentes de forma que el frontend pueda procesar
            
            Params:
                documents(list)
                metadatas(list)
                
            """

            formatted_sources = []
            for doc, meta in zip(documents, metadatas):
                formatted_sources.append({
                    "title": meta.get('source'),
                    "link": meta.get('link', '#'),
                    "content": doc,
                })
            return formatted_sources
    
 
            
        formatted_sources = _format_sources(documents, metadatas)
        yield {"type": "final", "sources": formatted_sources, "query": query}



# def main():
#     file_path = "lidax_pdf/08 - INT_LDX_ISD_TEC_009__2-1_Diseño de Taladros.pdf"


#     from LLM import Ollama_LLM
#     from E_Model import Ollama_Embedding
#     from Image_Model import Visual_Ollama
#     from sentence_transformers import CrossEncoder
#     from langchain_text_splitters import MarkdownTextSplitter

    
#     TEXT_SPLITTER =  MarkdownTextSplitter()# TextSplitter.from_tiktoken_model("gpt-3.5-turbo", capacity=CHUNK_SIZE, overlap= CHUNK_OVERLAP)

#     RERANKER = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

#     TEXT_MODEL = Ollama_LLM("react-ollama-v4")
#     EMBED_MODEL = Ollama_Embedding("mxbai-embed-large")
#     IMAGE_MODEL = Visual_Ollama("llava:7b")

#     rag = Chroma_RAG(EMBED_MODEL,TEXT_MODEL,IMAGE_MODEL,TEXT_SPLITTER,RERANKER, print_documents= True)

#     print("Check 1")


#     text =rag.add_markdown([file_path])
#     print(text)


# if __name__ == "__main__":
#     main()