# Sistema RAG con Gestión de Documentos y Consultas Inteligentes

Un sistema de Retrieval-Augmented Generation (RAG) que permite gestionar documentos y realizar consultas inteligentes usando ChromaDB como base de datos vectorial.

## Funcionalidad

1. Procesamiento de Documentos: PDF, DOCX, DOC, TXT, MD, RTF
2. Gestión de Memoria: Historial de conversación persistente
3. Reranking: Reordenamiento inteligente de documentos
4. Interfaz RAG: Fácil extensión para nuevos modelos
5. Soporte Multi-proveedor: OpenAI, Ollama y Google Gemini
6. Interfaz Web: Frontend React moderno

## Instrucciones

### 1. Instalar Dependencias

Recomendado hacerlo en un venv:

pip install -r requirements.txt


### 2. Configurar Frontend React

cd frontend
npm install
npm run dev

### 3. Para OpenAI:

3.1 Conseguir llave API de OpenAI: https://platform.openai.com/

3.2 Poner en terminal si usas bash:

export OPENAI_API_KEY="tu-api-key"

Para Windows:

set OPENAI_API_KEY=tu-api-key-aqui

O configurar directamente en el código:

En OpenAI_RAG, linea 37:

client = OpenAI(api_key="tu-api-key-aqui")


### 4. Para Google Gemini:

4.1 Conseguir llave API de Google Gemini: https://aistudio.google.com/

4.2 Poner en terminal si usas bash:

export GEMINI_API_KEY="tu-api-key-gemini"

Para Windows:

set GEMINI_API_KEY=tu-api-key-gemini


### 5. Para Ollama:

5.1 Instalar Ollama: https://ollama.ai/

5.2 Instalar modelos que necesites desde la CLI o usando:

ollama pull "nombre_modelo"


5.3 (Opcional) Usar el Modelfile dado con comando:

ollama create nombre_modelo -f ./Modelfile


### 6. Ejecutar el Sistema

Asegurarse que ollama esta corriendo en el PC

python main.py

./rag_inferface - npm start


El servidor estará disponible en http://localhost:8000 y la interfaz React en http://localhost:3000