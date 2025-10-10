
from Chroma_Rag import Chroma_Rag


class GeminiRag(Chroma_Rag):

    def __init__(self, embedding_model, llm, vector_store, text_splitter, reranker = None, k = 5):


        super().__init__(embedding_model, llm, vector_store, text_splitter, reranker, k)


    def invoke(self, query:str):
        pass

    def invoke_rerank(self, query:str):
        pass

    def get_embeddings(self, text:str):
        pass

