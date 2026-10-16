from pathlib import Path
from typing import List
from dotenv import load_dotenv
import os
import certifi

load_dotenv()

os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from pypdf import PdfReader
import docx2txt


Path("uploads").mkdir(exist_ok=True)
Path("chroma_db").mkdir(exist_ok=True)


# Embeddings model
embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")

vectorstore = Chroma(
    collection_name="agentic_chatbot_docs",
    embedding_function=embeddings,
    persist_directory="chroma_db"
)



def read_file_text(file_path: str) -> str:
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        reader = PdfReader(file_path)
        text = ""

        for page in reader.pages:
            text += page.extract_text() or ""
            text += "\n"

        if len(text.strip()) >= 200:
            return text

        try:
            import pymupdf
            import pytesseract
            from PIL import Image
        except ImportError as error:
            raise ValueError(
                "This PDF appears to be scanned or image-based. Install PyMuPDF, "
                "Pillow, pytesseract, and the Tesseract OCR engine before uploading it."
            ) from error

        ocr_text = []
        pdf = pymupdf.open(file_path)

        try:
            for page in pdf:
                pixmap = page.get_pixmap(matrix=pymupdf.Matrix(2, 2), alpha=False)
                image = Image.frombytes("RGB", [pixmap.width, pixmap.height], pixmap.samples)
                page_text = pytesseract.image_to_string(image).strip()

                if page_text:
                    ocr_text.append(page_text)
        finally:
            pdf.close()

        text = "\n\n".join(ocr_text)

        if not text.strip():
            raise ValueError("No readable text could be extracted from this PDF.")

        return text

    if suffix == ".docx":
        return docx2txt.process(file_path)

    if suffix in [".txt", ".md", ".py", ".csv"]:
        return path.read_text(encoding="utf-8", errors="ignore")

    raise ValueError("Unsupported file type. Upload PDF, DOCX, TXT, MD, PY, or CSV.")




def add_document_to_rag(file_path: str, thread_id: str, display_name: str | None = None):
    text = read_file_text(file_path)

    if not text.strip():
        raise ValueError("No text could be extracted from this file.")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=900,
        chunk_overlap=150
    )

    chunks = splitter.split_text(text)

    docs: List[Document] = [
        Document(
            page_content=chunk,
            metadata={
                "thread_id": thread_id,
                "source": display_name or Path(file_path).name
            }
        )
        for chunk in chunks
    ]

    vectorstore.delete(where={"thread_id": thread_id})
    vectorstore.add_documents(docs)

    return {
        "filename": display_name or Path(file_path).name,
        "chunks": len(docs)
    }





def retrieve_from_rag(query: str, thread_id: str, k: int = 3, max_chars: int = 4200) -> str:
    docs = vectorstore.similarity_search(
        query,
        k=k,
        filter={"thread_id": thread_id}
    )

    if not docs:
        return "No relevant uploaded document content found."

    results = []
    total_chars = 0

    for i, doc in enumerate(docs, start=1):
        source = doc.metadata.get("source", "uploaded document")
        remaining = max_chars - total_chars

        if remaining <= 0:
            break

        content = doc.page_content[:remaining]
        results.append(f"[Source {i}: {source}]\n{content}")
        total_chars += len(content)

    if len(results) < len(docs):
        results.append("[Context shortened to fit the model context window.]" )

    return "\n\n".join(results)