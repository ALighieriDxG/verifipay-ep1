"""Carga de documentos y construcción de índices FAISS."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from langchain_classic.schema import Document
from langchain_classic.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

from src.config import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    EXTERNAL_DIR,
    EXTERNAL_INDEX_PATH,
    INTERNAL_DIR,
    INTERNAL_INDEX_PATH,
    LLM_API_KEY,
    LLM_BASE_URL,
    EMBEDDING_MODEL,
    STORAGE_DIR,
)


def get_embeddings() -> OpenAIEmbeddings:
    return OpenAIEmbeddings(
        base_url=LLM_BASE_URL,
        api_key=LLM_API_KEY,
        model=EMBEDDING_MODEL,
        check_embedding_ctx_length=False,
    )


def _read_markdown_files(directory: Path, source_type: str) -> list[Document]:
    documents: list[Document] = []
    for path in sorted(directory.glob("*.md")):
        content = path.read_text(encoding="utf-8")
        documents.append(
            Document(
                page_content=content,
                metadata={"source": path.name, "tipo": source_type, "formato": "markdown"},
            )
        )
    return documents


def _read_faq(path: Path) -> list[Document]:
    items = json.loads(path.read_text(encoding="utf-8"))
    docs: list[Document] = []
    for item in items:
        text = f"Pregunta: {item['pregunta']}\nRespuesta: {item['respuesta']}"
        docs.append(
            Document(
                page_content=text,
                metadata={
                    "source": path.name,
                    "tipo": "interno",
                    "categoria": item.get("categoria", "general"),
                    "formato": "faq",
                },
            )
        )
    return docs


def _read_tickets(path: Path) -> list[Document]:
    docs: list[Document] = []
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            text = (
                f"Ticket {row['ticket_id']} ({row['categoria']}): "
                f"{row['consulta']} -> {row['resolucion']}"
            )
            docs.append(
                Document(
                    page_content=text,
                    metadata={
                        "source": path.name,
                        "tipo": "interno",
                        "categoria": row["categoria"],
                        "formato": "ticket",
                        "referencia": row.get("fuente", ""),
                    },
                )
            )
    return docs


def load_internal_documents() -> list[Document]:
    docs = _read_markdown_files(INTERNAL_DIR, "interno")
    docs.extend(_read_faq(INTERNAL_DIR / "faq_comercios.json"))
    docs.extend(_read_tickets(INTERNAL_DIR / "tickets_resueltos.csv"))
    return docs


def load_external_documents() -> list[Document]:
    return _read_markdown_files(EXTERNAL_DIR, "externo")


def split_documents(documents: list[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
    )
    return splitter.split_documents(documents)


def build_vector_store(documents: list[Document], embeddings: OpenAIEmbeddings) -> FAISS:
    chunks = split_documents(documents)
    return FAISS.from_documents(chunks, embeddings)


def save_vector_store(store: FAISS, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    store.save_local(str(path))


def load_vector_store(path: Path, embeddings: OpenAIEmbeddings) -> FAISS:
    return FAISS.load_local(str(path), embeddings, allow_dangerous_deserialization=True)


def build_indexes(force: bool = False) -> tuple[FAISS, FAISS]:
    embeddings = get_embeddings()

    if force or not INTERNAL_INDEX_PATH.exists():
        internal_store = build_vector_store(load_internal_documents(), embeddings)
        save_vector_store(internal_store, INTERNAL_INDEX_PATH)
    else:
        internal_store = load_vector_store(INTERNAL_INDEX_PATH, embeddings)

    if force or not EXTERNAL_INDEX_PATH.exists():
        external_store = build_vector_store(load_external_documents(), embeddings)
        save_vector_store(external_store, EXTERNAL_INDEX_PATH)
    else:
        external_store = load_vector_store(EXTERNAL_INDEX_PATH, embeddings)

    return internal_store, external_store


def ensure_indexes(force: bool = False) -> tuple[FAISS, FAISS]:
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    return build_indexes(force=force)
