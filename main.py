import streamlit as st
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
import os
import io

# PDF / DOCX reading
from pypdf import PdfReader
import docx

from prompts import chat_prompt, DOCUMENT_PROMPT

load_dotenv()

# ── LLM setup ───────────────────────────────────────────────────────────────
def get_api_key():
    try:
        return st.secrets["GOOGLE_API_KEY"]   # Streamlit Cloud
    except Exception:
        return os.getenv("GOOGLE_API_KEY")    # local .env


def get_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.3,
        google_api_key=get_api_key(),
    )

# ── Text extraction helpers ──────────────────────────────────────────────────
def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract all text from a PDF file given its bytes."""
    reader = PdfReader(io.BytesIO(file_bytes))
    text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"
    return text.strip()


def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract all text from a DOCX file given its bytes."""
    doc = docx.Document(io.BytesIO(file_bytes))
    paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
    return "\n".join(paragraphs).strip()


def extract_text_from_file(file_bytes: bytes, filename: str) -> str:
    """Route to the correct extractor based on file extension."""
    ext = filename.lower().split(".")[-1]
    if ext == "pdf":
        return extract_text_from_pdf(file_bytes)
    elif ext in ("docx", "doc"):
        return extract_text_from_docx(file_bytes)
    elif ext == "txt":
        return file_bytes.decode("utf-8", errors="ignore")
    else:
        raise ValueError(f"Unsupported file type: .{ext}")


# ── Chat helpers ─────────────────────────────────────────────────────────────
def build_chat_history(history: list[dict]) -> list:
    """Convert Streamlit session history to LangChain message objects."""
    messages = []
    for msg in history:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        else:
            messages.append(AIMessage(content=msg["content"]))
    return messages


def analyze_document(file_bytes: bytes, filename: str, chat_history: list[dict]) -> str:
    """Analyze an uploaded legal document and return structured breakdown."""
    document_text = extract_text_from_file(file_bytes, filename)

    if not document_text:
        return "❌ Could not extract text from the uploaded file. Please ensure it is not scanned/image-based."

    llm = get_llm()
    chain = DOCUMENT_PROMPT | llm | StrOutputParser()

    response = chain.invoke({
        "document_text": document_text,
        "chat_history": build_chat_history(chat_history),
    })
    return response


def chat_with_bot(user_input: str, chat_history: list[dict]) -> str:
    """Send a user message and get a response with full conversation memory."""
    llm = get_llm()
    chain = chat_prompt | llm | StrOutputParser()

    response = chain.invoke({
        "input": user_input,
        "chat_history": build_chat_history(chat_history),
    })
    return response
