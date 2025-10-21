
from file_readers import smart_doc_processing, expand_directories
from chromadb import PersistentClient, errors
from model_interfaces import ConversationMemory, LLM, E_Model, Image_Model
from typing import Iterator
from typing import List, Any
import hashlib
from typing import Iterator



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
                embedding_model: E_Model, 
                llm: LLM, 
                image_model: Image_Model,
                text_splitter: Any, 
                reranker: Any= None,
                k: int= 5,
                top_k: int= 3,
                print_documents: bool = False):
        
        self.embedding_model = embedding_model
        self.llm = llm
        self.image_model = image_model
        self.text_splitter = text_splitter
        self.reranker = reranker
        self.k = k
        self.top_k = top_k
        self.print_documents = print_documents

        self.conversation_memory = ConversationMemory.ConversationMemory()

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
    
    

    def invoke(self, query: str) -> None:
        """
        Metodo para ejecutar la aquitectura RAG. Imprime la respuesta en consola.

        Params:
        query(str): Input de usuario

        """

        self.conversation_memory.add_message("user",query)

        relevant_messages = self.conversation_memory.get_full_history()

        conversation_history = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in relevant_messages])

        enhanced_query = self.llm.enhance_query(query, conversation_history)

        results = self.retrieve(enhanced_query)
        documents = results['documents'][0]
        metadatas = results.get('metadatas', [[]])[0]

        context = "\n".join([f"Document {i+1}: {doc}" for i, doc in enumerate(documents)])

        if self.reranker:
            
            reranked_docs, reranked_metadatas = self.rerank_documents(query, documents, metadatas)
            documents = reranked_docs[:self.top_k]
            metadatas = reranked_metadatas[:self.top_k]

        manual_prompt = f"""Task: ANSWER: Using only the provided context
        Context: {context}

        Question: {enhanced_query}

        Answer:"""

        stream = self.llm.generate_stream(manual_prompt)

        full_response = self.llm.get_full_response(stream, bool_print=True)

        if full_response:

            self.conversation_memory.add_message("system", full_response)

        if self.print_documents:

            print("\nDocuments used:")
            for i, metadata in enumerate(metadatas):
                file_path = metadata.get('source', f"Document {i+1}")
                print(f"\nDocument {i+1}: {file_path}")



    def invoke_for_testing(self, query: str) -> dict:
        """
        Metodo para ejecutar la aqruitectura RAG. Devuelve la respuesta en un dict que REACT puede interpretar.

        Params:
        query(str): Input de usuario

        Return -> dict

        {
            "answer": full_response, (str)
            "sources": sources,  (List[Dict]) ->   {"id": int, "title": str, "content": str}
            "query": query  (str)
        }

        """
        
        self.conversation_memory.add_message("user",query)

        relevant_messages = self.conversation_memory.get_full_history()

        conversation_history = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in relevant_messages])

        enhanced_query = self.llm.enhance_query(query,conversation_history)

        results = self.retrieve(enhanced_query)
        documents = results['documents'][0]
        metadatas = results.get('metadatas', [[]])[0]

        if self.reranker:

            reranked_docs, reranked_metadatas = self.rerank_documents(query, documents, metadatas)
            documents = reranked_docs[:self.top_k]
            metadatas = reranked_metadatas[:self.top_k]
            
        context = "\n".join([f"Document {i+1}: {doc}" for i, doc in enumerate(documents)])

        manual_prompt= f"""Task: ANSWER: Using only the provided context
        Context: {context}

        Question: {enhanced_query}

        Answer:"""

        stream = self.llm.generate_stream(manual_prompt)

        full_response = self.llm.get_full_response(stream)

        if full_response:

            self.conversation_memory.add_message("system", full_response)

        sources = []

        for i, (metadata, doc_content) in enumerate(zip(metadatas, documents)):
            sources.append({
                "id": i + 1,
                "title": metadata.get('source', f"Document {i+1}"),
                "content": doc_content
                #"content": doc_content[:200] + "..." if len(doc_content) > 200 else doc_content
            })
        
        return {
            "answer": full_response,
            "sources": sources,  
            "query": query  
        }
    

    def _format_sources(self, documents: list, metadatas: list) -> list:

        formatted_sources = []
        for doc, meta in zip(documents, metadatas):
            formatted_sources.append({
                "title": meta.get('source'),
                "link": meta.get('link', '#'),
                "content": doc,
            })
        return formatted_sources
    


    def invoke_as_stream(self, query: str) -> Iterator[dict]:
        """
        Handles RAG logic and streams the response chunks and final sources 
        as structured dictionaries.
        """
        self.conversation_memory.add_message("user", query)
        
        # 1. Prepare RAG Context (Non-streaming part)
        relevant_messages = self.conversation_memory.get_full_history()
        conversation_history = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in relevant_messages])

        enhanced_query = self.llm.enhance_query(query,conversation_history)
        
        results = self.retrieve(enhanced_query)
        documents = results['documents'][0]
        metadatas = results['metadatas'][0]

        if self.reranker:
            reranked_docs, reranked_metadatas = self.rerank_documents(query, documents, metadatas)
            documents = reranked_docs[:self.top_k]
            metadatas = reranked_metadatas[:self.top_k]
        
        context = "\n".join([f"Document {i+1}: {doc}" for i, doc in enumerate(documents)])

        manual_prompt = f"""Task: ANSWER: Using only the provided context
        Context: {context}

        Question: {enhanced_query}

        Answer:"""

        # 2. Get the LLM stream (an iterator)
        llm_stream = self.llm.generate_stream(manual_prompt) # This calls ollama.generate(..., stream=True)

        # 3. Stream text chunks as structured data
        full_response = ""
        for chunk in llm_stream:
            # 🛑 Ensure 'chunk' here is a dictionary, not a string representation of one 🛑
            # If it's a string, you might have to parse it, but that's complex and usually unnecessary.
            
            # Assuming it IS a dictionary:
            chunk_text = chunk.get('response', '') 
            
            # 🛑 Yield a dictionary 🛑
            yield {"type": "chunk", "content": chunk_text}

            # Accumulate text for memory
            full_response += chunk_text

        # 4. Update memory AFTER the stream is fully consumed
        if full_response:
            self.conversation_memory.add_message("system", full_response)
            
        # 5. Calculate and yield final sources JSON
        formatted_sources = self._format_sources(documents, metadatas)
        # 🛑 Yield the final dictionary containing sources 🛑
        yield {"type": "final", "sources": formatted_sources, "query": query}



