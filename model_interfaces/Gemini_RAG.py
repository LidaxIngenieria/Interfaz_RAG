
from model_interfaces.Chroma_RAG import Chroma_RAG
from google import genai
from typing import List, Any

#export GEMINI_API_KEY

class Gemini_RAG(Chroma_RAG):
    """
    Implementación concreta de Chroma_RAG utilizando la API de Gemini(google.genai) para embeddings y generación.
    Proporciona funcionalidad RAG con los modelos de Gemini.

    Params:
        embedding_model (str): Nombre del modelo de embeddings de Gemini.
        llm (str): Nombre del modelo de lenguaje de Gemini.
        text_splitter (Any): Divisor de texto para procesamiento de documentos.
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
                k: int = 5, 
                top_k: int = 3,
                print_documents: bool = False):

        self.client = genai.Client()

        super().__init__(embedding_model, llm, text_splitter, reranker, k, top_k, print_documents)

    
    

    def get_embeddings(self, text:str) -> List[float]:
        """
        Genera embeddings para el texto usando el modelo de Gemini especificado.

        Params:
            text (str): Texto para generar embeddings
        """

        result = self.client.models.embed_content(
            model=self.embedding_model,
            contents=text,
        )

        return result
    
    def generate_stream(self, prompt: str):
        """
        Genera respuesta con el modelo de Gemini, devuelve la respuesta como stream usando el prompt pasado como parametro.
        
        Params:
            prompt (str): Texto que se pasa al modelo como prompt para generar respuesta
        """

        stream = self.client.models.generate_content_stream(
            self.llm,
            contents= prompt

        )

        return stream
    
    def get_full_response(self, stream, bool_print: bool = False) -> str:
        """
        Método devuelve la respuesta completa de un modelo a partir del stream.
        
        Params:
            stream: stream de la respuesta generada por el modelo
            bool_print(bool): boolean para imprimir el texto del stream a la consola.
        """

        full_response = ""
        for chunk in stream:
            if chunk.text:
                if bool_print:
                    print(chunk.text, end='', flush=True)
                full_response += chunk.text

        return full_response

 