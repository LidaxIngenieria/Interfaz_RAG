from abc import ABC, abstractmethod
from typing import List
import ollama


class E_Model(ABC):


    def __init__(self, 
                 model_name: str):
        
        self.model_name = model_name


    @abstractmethod
    def generate_embeddings(self,texts: List[str]):
        pass

class OpenAI_Embedding(E_Model):

    def __init__(self, 
                 model_name: str,
                 client):
        
        self.client = client
        super().__init__(model_name)

        
class Ollama_Embedding(E_Model):

    def __init__(self,
                 model_name: str):
        
        super().__init__(model_name)

    def generate_embeddings(self, texts: List[str]):
        """
        Genera embeddings para el texto usando el modelo de Ollama especificado.

        Params:
            texts (List[str]): Texto para generar embeddings

        """
       
        response = ollama.embed(model=self.model_name, input=texts)
        return response['embeddings']