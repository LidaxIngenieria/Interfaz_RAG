from model_interfaces import Chroma_RAG, LLM, E_Model, Image_Model
from semantic_text_splitter import TextSplitter
from sentence_transformers import CrossEncoder
import time
import os

CHUNK_SIZE = 1200
CHUNK_OVERLAP = 200


TEST_FILE = "./test_prompts.txt"

OUTPUT_DIR = "respuestas_txt" #carpeta donde se guardan los archivos txt


def main():

    TEXT_SPLITTER = TextSplitter.from_tiktoken_model("gpt-3.5-turbo", capacity=CHUNK_SIZE, overlap= CHUNK_OVERLAP)

    RERANKER = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

    #rag



    rag_models = []


    for rag in rag_models:
        file_list = ["./lidax_pdf"]
        rag.add_documents(file_list)
        with open(TEST_FILE, "r", encoding="utf-8") as txt_file:
            text = txt_file.read()

        paragraphs = text.split("\n")

        os.makedirs(OUTPUT_DIR, exist_ok=True)

        output_file = f"{OUTPUT_DIR}/respuestas_{rag.llm}_{rag.embedding_model}_{rag.k}_{rag.top_k}.txt"


        with open(output_file, 'w', encoding='utf-8') as file:

            file.write(f"Respuestas de {rag.llm} with {rag.embedding_model}\n\n")
            file.write(f"Parametros: k={rag.k}, top_k={rag.top_k}, chunk_size={CHUNK_SIZE}, chunk_overlap={CHUNK_OVERLAP}\n\n")

            total_time = 0

            for i, paragraph in enumerate(paragraphs):
                start = time.time()
                dict_response = rag.invoke_for_testing(paragraph)
                end = time.time()
                elapsed = end - start
                total_time += elapsed

                chunks_used = dict_response.get("sources")

                source_docs = f""
                for chunk in chunks_used:
                    title = chunk.get("title")
                    content = chunk.get("content")
                    source_docs += f"\n\nChunk from: {title}\nContent: {content}\n\n"
                    
                
                file.write(f"Pregunta: {i+1}:\n{paragraph}...\n\n")
                file.write(f"Respuesta: {dict_response.get("answer")}\n\n")
                file.write(f"Chunks Usados: {source_docs}\n\n")
                file.write(f"Tiempo: {elapsed}\n\n")
                file.write("=" * 90 + "\n\n")


if __name__ == "__main__":
    main()


