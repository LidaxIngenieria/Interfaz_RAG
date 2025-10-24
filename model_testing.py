from model_interfaces.Chroma_RAG import Chroma_RAG
from model_interfaces.LLM import Ollama_LLM
from model_interfaces.E_Model import Ollama_Embedding
from model_interfaces.Image_Model import Visual_Ollama
from semantic_text_splitter import TextSplitter
from sentence_transformers import CrossEncoder
from langchain_text_splitters import MarkdownTextSplitter
import time
import os

CHUNK_SIZE = 1200
CHUNK_OVERLAP = 200


TEST_FILE = "./test_prompts.txt"

OUTPUT_DIR = "respuestas_txt" #carpeta donde se guardan los archivos txt


def main():

    TEXT_SPLITTER =  MarkdownTextSplitter()# TextSplitter.from_tiktoken_model("gpt-3.5-turbo", capacity=CHUNK_SIZE, overlap= CHUNK_OVERLAP)

    RERANKER = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

    TEXT_MODEL = Ollama_LLM("react-ollama-v4")
    EMBED_MODEL = Ollama_Embedding("mxbai-embed-large")
    IMAGE_MODEL = Visual_Ollama("llava:7b")

    rag = Chroma_RAG(EMBED_MODEL,TEXT_MODEL,IMAGE_MODEL,TEXT_SPLITTER,RERANKER, print_documents= True)



    rag_models = [rag]


    for rag in rag_models:
        file_list = ["./lidax_pdf"]
        re_txt = rag.add_markdown(file_list)
        print(re_txt)
        with open(TEST_FILE, "r", encoding="utf-8") as txt_file:
            text = txt_file.read()

        paragraphs = text.split("\n")

        os.makedirs(OUTPUT_DIR, exist_ok=True)

        output_file = f"{OUTPUT_DIR}/respuestas_{rag.llm.model_name}_{rag.embedding_model.model_name}_{rag.k}_{rag.top_k}.txt"


        with open(output_file, 'w', encoding='utf-8') as file:

            file.write(f"Respuestas de {rag.llm.model_name} with {rag.embedding_model.model_name}\n\n")
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


