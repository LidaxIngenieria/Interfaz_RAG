from model_interfaces.Chroma_RAG import Chroma_RAG
from typing import Any, List
import ollama

class Ollama_RAG(Chroma_RAG):

    """
    Implementación concreta de Chroma_RAG utilizando Ollama para embeddings y generación.
    Proporciona funcionalidad RAG con modelos locales a través de Ollama.

    Params:
        embedding_model (str): Nombre del modelo de embeddings de Ollama.
        llm (str): Nombre del modelo de lenguaje de Ollama.
        vector_store (Any): Almacén vectorial ChromaDB.
        text_splitter (Any): Divisor de texto para procesamiento de documentos
        reranker (Any, optional): Modelo de reranking para reordenar documentos.
        k (int, optional): Número de documentos a recuperar. Por defecto 5.
        top_k(int,opcional): Número de documentos que se usan después del rerank si se a proporcionado un reranker. Por defecto 3.
        print_documents(bool,opcional): Boolean por si queres que imprime los chunks que se usaron para generar la respuesta. Por defecto False.

    """


    def __init__(self, 
                embedding_model: str,
                llm: str,
                text_splitter: Any, 
                reranker: Any = None,
                k: int= 5,
                top_k: int= 3,
                print_documents: bool = False):


        super().__init__(embedding_model, llm, text_splitter, reranker, k, top_k, print_documents)



    def get_embeddings(self, text: str) -> List[float]:
        """
        Genera embeddings para el texto usando el modelo de Ollama especificado.

        Params:
            text (str): Texto para generar embeddings

        """
        response = ollama.embed(model=self.embedding_model, input=text)
        return response['embeddings'][0]
    
    
    def generate_stream(self, prompt: str):
        """
        Genera respuesta con el modelo de Ollama, devuelve la respuesta como stream usando el prompt pasado como parametro.
        
        Params:
            prompt (str): Texto que se pasa al modelo como prompt para generar respuesta
        """

        stream = ollama.generate(
            model=self.llm,
            prompt= prompt,
            stream=True
        )

        return stream
    
    def get_full_response(self, stream, bool_print: bool = False) -> str:
        """
        Método que devuelve la respuesta completa de un modelo a partir del stream.
        
        Params:
            stream: stream de la respuesta generada por el modelo
            bool_print(bool): boolean para imprimir el texto del stream a la consola.
        """
                
        full_response = "\n"  
        for chunk in stream:
            response_text = chunk['response']
            if bool_print:
                print(chunk['response'], end='', flush=True)
            full_response += response_text

        return full_response
    
