from Chroma_Rag import Chroma_Rag
from openai import OpenAI
from typing import Any

# export "OPENAI_API_KEY" = ""

SYSTEM_PROMPT = """You are an expert research assistant. Follow these rules strictly:
1. Answer questions using ONLY the provided context
2. If context is insufficient, clearly state what information is missing
3. Cite relevant parts of the context in your response
4. Never hallucinate or invent information"""

class OpenAI_Rag(Chroma_Rag):
    """
    Implementación concreta de Chroma_Rag utilizando OpenAI para embeddings y generación.
    Proporciona funcionalidad RAG con los modelos de OpenAI.

     Params:
        embedding_model (str): Nombre del modelo de embeddings de OpenAI (ej: "text-embedding-ada-002")
        llm (str): Nombre del modelo de lenguaje de OpenAI (ej: "gpt-4", "gpt-3.5-turbo")
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
                k: int = 5):
        
        self.client = OpenAI()

        super().__init__(embedding_model, llm, vector_store, text_splitter, reranker, k)

    
    def get_embeddings(self, text: str) -> str:
        """
        Genera embeddings para el texto usando el modelo de OpenAI especificado.

        Params:
            text (str): Texto para generar embeddings
        """
        response = self.client.embeddings.create(
            model=self.embedding_model, 
            input=text
        )
        return response.data[0].embedding
    
    
    def invoke(self,query: str) -> None:
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

        stream = self.client.chat.completions.create(
            model=self.llm,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": manual_prompt}
            ],
            stream=True,
        )

                    
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                print(chunk.choices[0].delta.content, end='', flush=True)

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

        stream = self.client.chat.completions.create(
            model=self.llm,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": manual_prompt}
            ],
            stream=True,
        )

        full_response = "\n"   
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                response_text = chunk.choices[0].delta.content
                print(chunk.choices[0].delta.content, end='', flush=True)
                full_response += response_text
        
        self.conversation_memory.add_message("system", full_response)

        print("\nDocuments used:")
        for i, metadata in enumerate(top_metadatas):
            file_path = metadata.get('source', f"Document {i+1}")
            print(f"\nDocument {i+1}: {file_path}")
