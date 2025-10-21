from model_interfaces import Chroma_RAG, LLM, E_Model, Image_Model
from semantic_text_splitter import TextSplitter
from sentence_transformers import CrossEncoder

CHUNK_SIZE = 1200
CHUNK_OVERLAP = 200



def main():

    EMBED_MODEL = E_Model.Ollama_Embedding("nomic-embed-text")

    LLM_MODEL = LLM.Ollama_LLM("react_ollama_model")

    IMAGE_MODEL = Image_Model.Image_Model("None")

    TEXT_SPLITTER = TextSplitter.from_tiktoken_model("gpt-3.5-turbo", capacity=CHUNK_SIZE, overlap= CHUNK_OVERLAP)

    RERANKER = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

    rag = Chroma_RAG(EMBED_MODEL,LLM_MODEL, IMAGE_MODEL, TEXT_SPLITTER, RERANKER,k=7,top_k=3,print_documents=True)


    while True:
        try:
            command = input("\nInsert command (type 'h' for commands): ").split()
            if command[0] == "h":
                print(
                    "\nh-- print commands"
                    "\nask -- access Llama LLM"
                    "\nup <file_path>  -- upload text document to vector store"
                    "\nupdate <file_path>  -- update a document that is already in the store"
                    "\ndel <file_path>  -- delete a document from the store"
                    "\nq -- stop running script"
                )
            elif command[0] == "q":
                print("\nQuitting program")
                break

            elif command[0] == "up":
                print(rag.add_documents(command[1:]))

            elif command[0] == "del":
                print(rag.delete_documents(command[1:]))

            elif command[0] == "update":
                print(rag.update_documents(command[1:]))

            elif command[0] == "ask":
                print("\nHello! Im your RAG assistant.")
                while True:
                    try:
                        query = input("\nQuestion(type 'exit' to go back to commands): ").strip()

                        if query.lower() == 'exit':
                            print("\nGoodbye! going back to command CLI")
                            break

                        if not query:
                            continue
                            
                        rag.invoke(query)
                    
                        print("\n" + "-" * 70)

                    except Exception as e:
                        print(f"\nAn error occurred: {e}")
                        continue

            elif not command:
                continue

            else:
                print("\nUnknown command. Type 'h' for help.")
        
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break


if __name__ == "__main__":
    main()

    
