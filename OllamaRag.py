from Chroma_Rag import Chroma_Rag
from typing import Any
import ollama

class OllamaRag(Chroma_Rag):
    """
    Implementación concreta de Chroma_Rag utilizando Ollama para embeddings y generación.
    Proporciona funcionalidad RAG con modelos locales a través de Ollama.

    Params:
        embedding_model (str): Nombre del modelo de embeddings de Ollama
        llm (str): Nombre del modelo de lenguaje de Ollama
        vector_store (Any): Almacén vectorial ChromaDB
        text_splitter (Any): Divisor de texto para procesamiento de documentos
        reranker (Any, optional): Modelo de reranking para reordenar documentos
        k (int, optional): Número de documentos a recuperar. Por defecto 5.

    """


    def __init__(self, 
                embedding_model: str,
                llm: str,
                vector_store: Any, 
                text_splitter: Any, 
                reranker: Any = None,
                k: int= 5):

        super().__init__(embedding_model, llm, vector_store, text_splitter, reranker,k)


    def get_embeddings(self, text: str) -> str:
        """
        Genera embeddings para el texto usando el modelo de Ollama especificado.

        Params:
            text (str): Texto para generar embeddings

        """
        response = ollama.embed(model=self.embedding_model, input=text)
        return response['embeddings'][0]
    

    def invoke(self, query: str) -> None:
        """
        Ejecuta una consulta RAG básica sin reranking ni historial de conversación.

        Params:
            query (str): Consulta del usuario a procesar
        """

        results = self.retrieve(query)
        documents = results['documents'][0]
        metadatas = results.get('metadatas', [[]])[0]

        context = "\n".join([f"Document {i+1}: {doc}" for i, doc in enumerate(documents)])

        manual_prompt = f"Context: {context}\n\nQuestion: {query}"

        stream = ollama.generate(
            model=self.llm,
            prompt=manual_prompt,
            stream=True
        )
            
        for chunk in stream:

            print(chunk['response'], end='', flush=True)

        print("\nDocuments used:")
        for i, metadata in enumerate(metadatas):
            file_path = metadata.get('source', f"Document {i+1}")
            print(f"\nDocument {i+1}: {file_path}")


    def invoke_rerank(self, query: str) -> None:
        """
        Ejecuta una consulta RAG con reranking y memoria de conversación.

        Params:
            query (str): Consulta del usuario a procesar
        """

        if not self.reranker:
            print("\nNo reranker passed using method invoke()")
            return self.invoke(query)
        
        self.conversation_memory.add_message("user",query)

        relevant_messages = self.conversation_memory.get_full_history()

        conversation_history = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in relevant_messages])

        init_results = self.retrieve(query)
        init_documents = init_results['documents'][0]
        init_metadatas = init_results.get('metadatas', [[]])[0]

        reranked_docs, reranked_metadatas = self.rerank_documents(query, init_documents, init_metadatas)
        top_documents = reranked_docs[:3]
        top_metadatas = reranked_metadatas[:3]
        
        context = "\n".join([f"Document {i+1}: {doc}" for i, doc in enumerate(top_documents)])

        manual_prompt = f"Context: {context}\n\nConversationHistory: {conversation_history} \n\nQuestion: {query}"

        stream = ollama.generate(
            model=self.llm,
            prompt=manual_prompt,
            stream=True
        )
                
        full_response = "\n"  
        for chunk in stream:
            response_text = chunk['response']
            print(chunk['response'], end='', flush=True)
            full_response += response_text
        
        self.conversation_memory.add_message("system", full_response)

        print("\nDocuments used:")
        for i, metadata in enumerate(top_metadatas):
            file_path = metadata.get('source', f"Document {i+1}")
            print(f"\nDocument {i+1}: {file_path}")
