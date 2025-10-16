from model_interfaces.Ollama_RAG import Ollama_RAG
from model_interfaces.OpenAI_RAG import OpenAI_RAG
from semantic_text_splitter import TextSplitter
from sentence_transformers import CrossEncoder
import csv
import time
import os

CHUNK_SIZE = 1200
CHUNK_OVERLAP = 200

TEXT_SPLITTER = TextSplitter.from_tiktoken_model("gpt-3.5-turbo", capacity=CHUNK_SIZE, overlap= CHUNK_OVERLAP)

RERANKER = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

TEST_FILE = "respuestas_csv/test_prompts.txt"

OUTPUT_DIR = "respuestas_csv" #carpeta donde se guardan los archivos csv

def main():

    rag_openai_10_3 = OpenAI_RAG("text-embedding-3-small", "gpt-3.5-turbo", TEXT_SPLITTER, RERANKER, k=10, top_k=3)
    rag_openai_10_5 = OpenAI_RAG("text-embedding-3-small", "gpt-3.5-turbo", TEXT_SPLITTER, RERANKER, k=10, top_k=5)
    #rag_ollama = OllamaRag("nomic-embed-text", "rag-memory-3", TEXT_SPLITTER, RERANKER, k=10, top_k=3)

    rag_models = [rag_openai_10_3, rag_openai_10_5]


    with open(TEST_FILE, "r", encoding="utf-8") as txt_file:
        text = txt_file.read()

    paragraphs = text.split("\n")

    for rag in rag_models:
        print(f"\nProcessing with model: {rag.llm} | Embedding: {rag.embedding_model} | k={rag.k}, top_k={rag.top_k}")

        file_list = ["./lidax_pdf"]
        rag.add_documents(file_list)




        fieldnames = ["question", "answer", "elapsed_time"]

        os.makedirs(OUTPUT_DIR, exist_ok=True)
        output_file = f"{OUTPUT_DIR}/respuestas_{rag.llm}_{rag.embedding_model}_{rag.k}_{rag.top_k}.csv"
        


        with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
        
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            total_time = 0
            for i, paragraph in enumerate(paragraphs):

                start = time.time()
                dict_response = rag.invoke_api(paragraph)
                end = time.time()
                elapsed = end - start
                total_time += elapsed

                answer = dict_response.get("answer")
                writer.writerow({
                    "question": paragraph,
                    "answer":answer,
                    "elapsed_time": elapsed
                })


        

        print(f"\nTime: {total_time}")


    print("\nAll models processed successfully.")


if __name__ == "__main__":
    main()








