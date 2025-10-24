
import ollama

from abc import ABC, abstractmethod
from openai import OpenAI




class Text_Model(ABC):


    def __init__(self,
                 model_name: str):
        
        self.model_name = model_name


    @abstractmethod
    def generate_stream(self,prompt:str):
        """
        Metodo abstracto para generar respuesta como stream en base an un prompt usando la LLM
        
        Params:
            prompt(str)
            
        """
        pass

    @abstractmethod
    def get_full_response(self,stream, bool_print:bool = False)-> str:
        """
        Metodo abstracto para transfoormar respuesta stream en en str
        
        Params:
            stream
            bool_print(bool): Para imprimir o no la respuesta completa en consola(para testng y debugging)
            
        """
        pass

    @abstractmethod
    def enhance_query(self, query:str, memory:str) -> str:
        """
        Metodo abstracto para mejorar un query y devolver un nuevo prompt 
        
        Params:
            quert(str)
            memory(str)

        """
            
        pass


class OpenAI_LLM(Text_Model):

    def __init__(self,
                 model_name: str,
                 client):
        
        self.client = client
        
        super().__init__(model_name)

    def generate_stream(self, prompt: str):
        """
        Metodo  para generar respuesta como stream en base an un prompt usando la LLM
        
        Params:
            prompt(str)
            
        """

        try:
        
            stream = self.client.chat.completions.create(
                model=self.llm,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                stream=True,
            )

            return stream
        
        except Exception as e:
            print(f"Error generating stream: {e}")
    
    def get_full_response(self, stream, bool_print: bool = False)-> str:
        """
        Metodo abstracto para transfoormar respuesta stream en en str
        
        Params:
            stream
            bool_print(bool): Para imprimir o no la respuesta completa en consola(para testng y debugging)
            
        """

        full_response = "\n"   
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                response_text = chunk.choices[0].delta.content
                if bool_print:
                    print(chunk.choices[0].delta.content, end='', flush=True)
                full_response += response_text

        return full_response
    
    #Implementacion opanai para enhance quey
    

class Ollama_LLM(Text_Model):

    def __init__(self,
                 model_name: str):
        
        super().__init__(model_name)


    def generate_stream(self, prompt: str):
        """
        Genera respuesta con el modelo de Ollama, devuelve la respuesta como stream usando el prompt pasado como parametro.
        
        Params:
            prompt (str): Texto que se pasa al modelo como prompt para generar respuesta
        """

        try:
        
            stream = ollama.generate(
                model=self.model_name,
                prompt= prompt,
                stream=True
            )

            return stream
        
        except Exception as e:
            print(f"Error generating stream: {e}")
        

    def get_full_response(self, stream, bool_print: bool = False)-> str:
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


    #Mejorar o cambiar por completo
    def enhance_query(self, query:str, memory:str):
        """
        Método para mejorar el input del usario anted de hacer la busqueda de vectores
        
        Params:
            query(str): Input del usuario
            memory(str): Texto representativo del historial de conversacion del usuario
        """

        prompt = f"""<s>[INST]
            You are a Query Rewriter assistant. Your task is to analyze a conversation history and a follow-up user query, and then generate a new, single, **standalone question**.

            The standalone question must be able to be understood and answered without needing the preceding conversation history. This ensures a more effective search in a vector database.

            If the follow-up query is already a standalone question (i.e., it doesn't rely on the history), simply return the follow-up query as is. Do not add any extra commentary or text.

            --- CONVERSATION HISTORY ---
            {memory}
            --- END HISTORY ---

            FOLLOW-UP QUERY: {query}

            STANDALONE QUESTION:
            [/INST]"""

        response = ollama.generate(
            model=self.model_name,
            prompt=prompt,
        )
    
        enhanced_query = response['response']

        print(f"\nENHANCED QUERY: {enhanced_query}\n\n{"-"*100}")
                    
        return enhanced_query
        

        
        
    


        