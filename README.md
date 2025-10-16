Un sistema de Retrieval-Augmented Generation (RAG) que permite gestionar documentos y realizar consultas inteligentes usando ChromaDB como base de datos vectorial.

Funcionalidad:

1.Procesamiento de Documentos: PDF, DOCX, DOC, TXT, MD, RTF
2.Gestión de Memoria: Historial de conversación persistente
3.Reranking: Reordenamiento inteligente de documentos
4.Interfaz RAG: Fácil extensión para nuevos modelos

Instrucciones

    1. Instalar depencdencias ->  pip install -r requirements.txt (Recomnedado hacerlo en un venv)

    2. Para OpenAI:

        2.1 Conseguir llave API de OpenAI -> https://platform.openai.com/

        2.2 Poner en terminal si usas bash -> export OPENAI_API_KEY="tu-api-key" 

            Para windows -> set OPENAI_API_KEY=tu-api-key-aqui

            O configurar directamente en el código:

            OpenAI_RAG, linea 37 client = OpenAI(api_key="tu-api-key-aqui")

    3. Para OLlama:

        3.1 Instalar Ollama -> https://ollama.ai/

        3.2 Instalar modelos que necesites desde la CLI o usando ollama pull "nombre_modelo"

        3.3(Opcional) Usar el Modelfile dado con comando -> ollama create nombre_modelo -f ./Modelfile


