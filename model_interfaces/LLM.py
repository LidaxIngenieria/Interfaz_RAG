from abc import ABC, abstractmethod
from openai import OpenAI
import ollama

SYSTEM_PROMPT = """You are an expert research assistant. Follow these rules strictly:
1. Answer questions using ONLY the provided context
2. If context is insufficient, clearly state what information is missing
3. Cite relevant parts of the context in your response
4. Never hallucinate or invent information
5.  You can use conversation history if provided but only use it if its relevant to current query, only cite retrieved documents"""


class LLM(ABC):


    def __init__(self,
                 model_name: str):
        
        self.model_name = model_name


    @abstractmethod
    def generate_stream(self,prompt:str):
        pass

    @abstractmethod
    def get_full_response(self,prompt:str)-> str:
        pass

    @abstractmethod
    def enhance_query(self, query:str, memory:str)-> str:
        pass


class OpenAI_LLM(LLM):

    def __init__(self,
                 model_name: str,
                 client):
        
        self.client = client
        
        super().__init__(model_name)

    def generate_stream(self, prompt: str):
        
        stream = self.client.chat.completions.create(
            model=self.llm,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            stream=True,
        )

        return stream
    
    def get_full_response(self, stream, bool_print: bool = False)-> str:

        full_response = "\n"   
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                response_text = chunk.choices[0].delta.content
                if bool_print:
                    print(chunk.choices[0].delta.content, end='', flush=True)
                full_response += response_text

        return full_response
    

class Ollama_LLM(LLM):

    def __init__(self,
                 model_name: str):
        
        super().__init__(model_name)


    def generate_stream(self, prompt: str):
        """
        Genera respuesta con el modelo de Ollama, devuelve la respuesta como stream usando el prompt pasado como parametro.
        
        Params:
            prompt (str): Texto que se pasa al modelo como prompt para generar respuesta
        """
        
        stream = ollama.generate(
            model=self.model_name,
            prompt= prompt,
            stream=True
        )

        return stream
    

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


    def enhance_query(self, query:str, memory:str):
        """
        Método para mejorar el input del usario anted de hacer la busqueda de vectores
        
        Params:
            query(str): Input del usuario
            memory(str): Texto representativo del historial de conversacion del usuario
        """

        prompt = f"""
        You are an intelligent query enhancer. Your ONLY job is to rewrite the user's question using relevant information from the conversation history — if and only if it's directly related.

        ### RULES:
        1. **DO NOT ANSWER THE QUESTION.** Only return a rewritten version of the question, maintaining the original intent.
        2. Only use information from the conversation history if it's RELEVANT to the current question. for example when the user input is ambigious or uses similar keywords.
        3. Do NOT include phrases like "based on the conversation" or "context".
        4. Your output MUST be a single, clean question — nothing else.
        5. Always make sure to keep the users intention with the original queston in mind when generating the enhanced version

        ### INPUTS

        Conversation History:
        {memory}

        Original Question:
        {query}

        ### YOUR TASK

        Rewrite the question, incorporating any relevant context:

        Enhanced Question:"""
        response = ollama.generate(
            model=self.model_name,
            prompt=prompt,
        )
    
        enhanced_query = response['response']

        print(f"\nENHANCED QUERY: {enhanced_query}\n\n{"-"*100}")
                    
        return enhanced_query
        

        
        
    


        