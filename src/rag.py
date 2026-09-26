"""Recuperación semántica y formateo de contexto RAG."""

from __future__ import annotations

from dataclasses import dataclass

from langchain_community.vectorstores import FAISS

from src.config import TOP_K


@dataclass
class RetrievalResult:
    query: str
    chunks: list[str]
    sources: list[str]
    scores: list[float]

    @property
    def context(self) -> str:
        blocks = []
        for idx, chunk in enumerate(self.chunks, start=1):
            source = self.sources[idx - 1] if idx - 1 < len(self.sources) else "desconocida"
            blocks.append(f"[Fragmento {idx} | Fuente: {source}]\n{chunk}")
        return "\n\n".join(blocks)

    @property
    def max_score(self) -> float:
        return max(self.scores) if self.scores else 0.0


def retrieve_with_scores(store: FAISS, query: str, k: int = TOP_K) -> RetrievalResult:
    docs_and_scores = store.similarity_search_with_score(query, k=k)
    chunks: list[str] = []
    sources: list[str] = []
    scores: list[float] = []

    for doc, score in docs_and_scores:
        chunks.append(doc.page_content)
        sources.append(str(doc.metadata.get("source", "desconocida")))
        # FAISS L2 distance: lower is better; convert to simple confidence proxy
        confidence = 1 / (1 + float(score))
        scores.append(confidence)

    return RetrievalResult(query=query, chunks=chunks, sources=sources, scores=scores)


def format_citations(result: RetrievalResult) -> str:
    unique_sources = sorted(set(result.sources))
    return ", ".join(unique_sources)
