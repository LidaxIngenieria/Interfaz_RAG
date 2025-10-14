from OllamaRag import OllamaRag
from OpenAI_Rag import OpenAI_Rag
from semantic_text_splitter import TextSplitter
from sentence_transformers import CrossEncoder
import time

CHUNK_SIZE = 1200
CHUNK_OVERLAP = 200


TEXT_SPLITTER = TextSplitter.from_tiktoken_model("gpt-3.5-turbo", capacity=CHUNK_SIZE, overlap= CHUNK_OVERLAP)

RERANKER = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

TEST_FILE = "./test_prompts.txt"


def main():

    rag_openai = OpenAI_Rag("text-embedding-3-small","gpt-3.5-turbo", TEXT_SPLITTER, RERANKER, k=10,top_k=3)

    rag_ollama = OllamaRag("nomic-embed-text","rag-memory-3",TEXT_SPLITTER, RERANKER,k=10,top_k=3)

    rag_models = [rag_openai,rag_ollama]


    for rag in rag_models:
        file_list = ["./lidax_pdf"]
        rag.add_documents(file_list)

        with open(TEST_FILE, "r", encoding="utf-8") as txt_file:
            text = txt_file.read()

        paragraphs = text.split("\n")

        output_file = f"tests_de_rag/respuestas_{rag.llm}_{rag.embedding_model}.txt"

        with open(output_file, 'w', encoding='utf-8') as file:

            file.write(f"Respuestas de {rag.llm} with {rag.embedding_model}\n\n")
            file.write(f"Parametros: k={rag.k}, top_k={rag.top_k}, chunk_size={CHUNK_SIZE}, chunk_overlap={CHUNK_OVERLAP}\n\n")

            for i, paragraph in enumerate(paragraphs):
                start = time.time()
                dict_response = rag.invoke_api(paragraph)
                end = time.time()
                elapsed = end - start

                chunks_used =dict_response.get("sources")

                source_docs = f""
                for chunk in chunks_used:
                    title = chunk.get("title")
                    content = chunk.get("content")
                    source_docs += f"\n\nChunk from: {title}\nContent: {content}\n\n"
                    
                
                file.write(f"Pregunta: {i+1}:\n{paragraph}...\n\n")
                file.write(f"Respuesta: {dict_response.get("answer")}\n\n")
                file.write(f"Chunks Usados: {source_docs}\n\n")
                file.write(f"Tiempo: {elapsed}\n\n")
                file.write("=" * 60 + "\n\n")


if __name__ == "__main__":
    main()


