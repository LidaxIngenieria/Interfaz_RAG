from model_interfaces.Chroma_RAG import Chroma_RAG
from openai import OpenAI
from typing import Any, List

# export "OPENAI_API_KEY" = ""

SYSTEM_PROMPT = """You are an expert research assistant. Follow these rules strictly:
1. Answer questions using ONLY the provided context
2. If context is insufficient, clearly state what information is missing
3. Cite relevant parts of the context in your response
4. Never hallucinate or invent information
5.  You can use conversation history if provided but only use it if its relevant to current query, only cite retrieved documents"""

class OpenAI_RAG(Chroma_RAG):
    """
    Implementación concreta de Chroma_RAG utilizando OpenAI para embeddings y generación.
    Proporciona funcionalidad RAG con los modelos de OpenAI.

     Params:
        embedding_model (str): Nombre del modelo de embeddings de OpenAI (ej: "text-embedding-ada-002").
        llm (str): Nombre del modelo de lenguaje de OpenAI (ej: "gpt-4", "gpt-3.5-turbo").
        text_splitter (Any): Divisor de texto para procesamiento de documentos.
        reranker (Any, opcional): Modelo de reranking para reordenar documentos.
        k (int, opcional): Número de documentos a recuperar. Por defecto 5.
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
        
        self.client = OpenAI()

        super().__init__(embedding_model, llm, text_splitter, reranker, k, top_k, print_documents)


    
    def get_embeddings(self, texts: List[str]) -> List[float]:
        """
        Genera embeddings para el texto usando el modelo de OpenAI especificado.

        Params:
            texts List[str]: Texto para generar embeddings
        """
        response = self.client.embeddings.create(
            model=self.embedding_model,
            input=texts
        )
        return [d.embedding for d in response.data]

    
    def generate_stream(self, prompt: str):
        """
        Genera respuesta con el modelo de OpenAI especifica, devuelve la respuesta como stream usando el prompt pasado como parametro.
        
        Params:
            prompt (str): Texto que se pasa al modelo como prompt para generar respuesta
        """
        stream = self.client.chat.completions.create(
            model=self.llm,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            stream=True,
        )

        return stream
    
    def get_full_response(self, stream, bool_print: bool = False) -> str:
        """
        Método  que devuelve la respuesta completa de un modelo a partir del stream.
        
        Params:
            stream: stream de la respuesta generada por el modelo
            bool_print(bool): boolean para imprimir el texto del stream a la consola.

        """

        full_response = "\n"   
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                response_text = chunk.choices[0].delta.content
                if bool_print:
                    print(chunk.choices[0].delta.content, end='', flush=True)
                full_response += response_text

        return full_response
        
  