# Custom-GPT

Custom-GPT is a personal AI chatbot built with Python and FastAPI. It has a ChatGPT-style interface, keeps conversation history, can search the web, and can answer questions about files uploaded in a chat.

I built it around LangGraph so the assistant can decide when to use a tool instead of treating every message as a simple prompt.

## What it can do

- Chat with several Groq models
- Stream responses as they are generated
- Keep separate conversations and chat history
- Upload and search PDF, DOCX, TXT, Markdown, Python, and CSV files
- Use RAG to answer questions from uploaded documents
- Search the web with Tavily for current information
- Save and recall useful information with long-term memory
- Perform basic calculations
- Store conversations, checkpoints, and document embeddings locally

## Tech used

- Python 3.11
- FastAPI and Uvicorn
- LangChain and LangGraph
- Groq for chat models
- Google Gemini embeddings
- Tavily for web search
- ChromaDB for document search
- SQLite for chat history, memory, and LangGraph checkpoints
- Jinja2 and plain HTML/CSS/JavaScript for the frontend

## Getting started

### 1. Clone the repository

```bash
git clone https://github.com/AnandVadgama/Custom-GPT.git
cd Custom-GPT
```

### 2. Create a virtual environment

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

On Windows, activate it with:

```powershell
.venv\Scripts\activate
```

### 3. Install the dependencies

```bash
pip install -r requirements.txt
```

### 4. Add environment variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-20b
GOOGLE_API_KEY=your_google_api_key
TAVILY_API_KEY=your_tavily_api_key
```

The app uses:

- `GROQ_API_KEY` for chat responses
- `GROQ_MODEL` for the default Groq model
- `GOOGLE_API_KEY` for Gemini document embeddings
- `TAVILY_API_KEY` for web search

Do not commit `.env` or any API keys to the repository.

### 5. Start the app

```bash
python app.py
```

Open [http://localhost:8080](http://localhost:8080) in your browser.

You can also start it directly with Uvicorn:

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8080
```

## Running with Docker

Build the image:

```bash
docker build -t custom-gpt .
```

Run it with your local `.env` file:

```bash
docker run --rm -p 8080:8080 --env-file .env custom-gpt
```

Then open [http://localhost:8080](http://localhost:8080).

## Uploading documents

The upload button accepts:

- PDF
- DOCX
- TXT
- Markdown
- Python
- CSV

Uploaded files are split into smaller chunks and stored in ChromaDB. When a question refers to an uploaded file, the assistant searches the relevant chunks before writing an answer.

Scanned PDFs may need OCR support. The Docker image already installs Tesseract. For a local setup, install Tesseract separately if you want to use image-based PDFs.

## Project structure

```text
.
├── agent.py                 # LangGraph agent and model configuration
├── app.py                   # FastAPI routes and response streaming
├── database.py              # SQLite models for chats and memory
├── rag.py                   # File reading, chunking, and document search
├── tools.py                 # Calculator, web search, memory, and RAG tools
├── templates/
│   └── index.html           # Chat interface
├── requirements.txt         # Python dependencies
└── Dockerfile               # Container setup
```

The `data/`, `chroma_db/`, and `uploads/` directories are created when the app runs. They contain local application data and are ignored by Git.

## Notes

- The default server runs on port `8080`.
- The default model is `openai/gpt-oss-20b`.
- If an unsupported model is selected, the app falls back to the default model.
- Each conversation has its own thread ID, so uploaded document context and chat history stay separated.

## License

This project is available under the license in [LICENSE](LICENSE).
