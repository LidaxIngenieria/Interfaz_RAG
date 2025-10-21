from model_interfaces import Chroma_RAG, LLM, E_Model, Image_Model
from semantic_text_splitter import TextSplitter
from sentence_transformers import CrossEncoder
import csv
import time
import os

CHUNK_SIZE = 1200
CHUNK_OVERLAP = 200


TEST_FILE = "test_prompts.txt"

OUTPUT_DIR = "respuestas_csv" #carpeta donde se guardan los archivos csv

def main():

    TEXT_SPLITTER = TextSplitter.from_tiktoken_model("gpt-3.5-turbo", capacity=CHUNK_SIZE, overlap= CHUNK_OVERLAP)

    RERANKER = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

    #rag

    rag_models = []


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
                dict_response = rag.invoke_for_testing(paragraph)
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








