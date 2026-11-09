"""Memoria de largo plazo: tickets en disco y recuperación por similitud.

El corpus documental sigue en los índices FAISS de la Evaluación 1. Esta capa
guarda los casos que el agente escribe y los recupera en un tercer índice.
Con clave de API el índice usa mistral-embed. Sin clave, o en las pruebas,
usa un vector de hashing de tokens para poder buscar igual en FAISS.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from pathlib import Path

import numpy as np
from langchain_classic.schema import Document
from langchain_community.vectorstores import FAISS
from langchain_core.embeddings import Embeddings

from src.config import LLM_API_KEY, MEMORY_DIR
from src.rag import retrieve_with_scores

_FOLD = str.maketrans("áéíóúüñ", "aeiouun")
_PAN = re.compile(r"(?:\d[ -]?){13,19}")
_CVV = re.compile(r"\bcvv\b", re.IGNORECASE)
_VACIO = {"", "ninguno", "n/a", "na", "sin id", "-"}


_STOP = {
    "ticket",
    "comercio",
    "transaccion",
    "estado",
    "consulta",
    "resumen",
    "fuentes",
    "sin",
    "id",
    "de",
    "la",
    "el",
    "y",
    "que",
    "con",
    "del",
    "los",
    "las",
    "un",
    "una",
    "por",
    "para",
    "en",
    "al",
    "lo",
    "se",
    "su",
    "es",
    "a",
    "o",
}


class HashEmbeddings(Embeddings):
    """Vectores dispersos por token. Sirven para pruebas y para el modo sin API."""

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [_hash_vec(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return _hash_vec(text)


def contiene_dato_sensible(texto: str) -> bool:
    return bool(_CVV.search(texto) or _PAN.search(texto or ""))


def _fold(text: str) -> str:
    return text.lower().translate(_FOLD)


def _hash_vec(text: str, dim: int = 128) -> list[float]:
    vec = np.zeros(dim, dtype=np.float32)
    for token in re.findall(r"[a-z0-9]+", _fold(text)):
        if token in _STOP or len(token) < 3:
            continue
        digest = hashlib.md5(token.encode("utf-8")).hexdigest()
        vec[int(digest, 16) % dim] += 1.0
    norma = float(np.linalg.norm(vec))
    if norma:
        vec /= norma
    return vec.tolist()


def _limpiar(valor: str) -> str:
    texto = (valor or "").strip()
    return "" if texto.lower() in _VACIO else texto


class MemoryStore:
    def __init__(self, root: Path | None = None, embedder: str = "auto"):
        self.root = Path(root) if root else MEMORY_DIR
        self.root.mkdir(parents=True, exist_ok=True)
        self.tickets_path = self.root / "tickets.jsonl"
        self.index_path = self.root / "faiss"
        self._marker = self.root / "embedder.txt"
        self._preferencia = embedder

    def reset(self) -> None:
        if self.tickets_path.exists():
            self.tickets_path.unlink()
        if self._marker.exists():
            self._marker.unlink()
        if self.index_path.exists():
            for path in self.index_path.glob("*"):
                path.unlink()
            self.index_path.rmdir()

    def listar(self) -> list[dict]:
        if not self.tickets_path.exists():
            return []
        tickets: list[dict] = []
        for line in self.tickets_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            tickets.append(json.loads(line))
        return tickets

    def registrar(
        self,
        comercio: str,
        consulta: str,
        resumen: str,
        estado: str,
        transaction_id: str = "",
        fuentes: str = "",
    ) -> str:
        crudo = " ".join((consulta, resumen, fuentes, transaction_id))
        if contiene_dato_sensible(crudo):
            resumen = "Solicitud de dato de tarjeta rechazada. No se almacenó el número ni el CVV."
            estado = "rechazado"
            fuentes = "pci_dss_resumen.md"
            transaction_id = ""
            consulta = "El comercio pidió transmitir un dato de tarjeta por el chat."

        estado = _estado(estado)
        ticket = {
            "ticket_id": self._siguiente_id(),
            "comercio": _limpiar(comercio) or "comercio no indicado",
            "consulta": consulta.strip(),
            "resumen": resumen.strip(),
            "estado": estado,
            "transaction_id": _limpiar(transaction_id).upper(),
            "fuentes": _limpiar(fuentes),
            "creado": datetime.now().isoformat(timespec="seconds"),
        }
        with self.tickets_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(ticket, ensure_ascii=False) + "\n")
        self._indexar(ticket)

        if estado == "rechazado":
            return (
                f"Rechazado: no se almacenan PAN ni CVV. "
                f"Quedó constancia en {ticket['ticket_id']} sin el dato."
            )
        return f"Ticket {ticket['ticket_id']} registrado con estado {estado}."

    def buscar(self, consulta: str, k: int = 3) -> str:
        tickets = self.listar()
        if not tickets:
            return "No hay casos anteriores en la memoria de largo plazo."
        try:
            if self.index_path.exists():
                return self._buscar_faiss(consulta, k)
        except Exception:
            pass
        return self._buscar_hash(consulta, k)

    def _modo(self) -> str:
        if self._marker.exists():
            return self._marker.read_text(encoding="utf-8").strip() or "hash"
        if self._preferencia == "hash":
            modo = "hash"
        elif self._preferencia == "mistral":
            modo = "mistral"
        else:
            modo = "mistral" if LLM_API_KEY else "hash"
        self._marker.write_text(modo, encoding="utf-8")
        return modo

    def _embeddings(self):
        if self._modo() == "mistral":
            from src.ingest import get_embeddings

            return get_embeddings()
        return HashEmbeddings()

    def _indexar(self, ticket: dict) -> None:
        try:
            self._agregar_documento(ticket)
        except Exception:
            if self._modo() == "mistral" and not self.index_path.exists():
                self._marker.write_text("hash", encoding="utf-8")
                self._agregar_documento(ticket)

    def _agregar_documento(self, ticket: dict) -> None:
        embeddings = self._embeddings()
        documento = Document(page_content=_nota(ticket), metadata={"ticket_id": ticket["ticket_id"]})
        if self.index_path.exists():
            store = FAISS.load_local(
                str(self.index_path),
                embeddings,
                allow_dangerous_deserialization=True,
            )
            store.add_documents([documento])
        else:
            store = FAISS.from_documents([documento], embeddings)
        self.index_path.mkdir(parents=True, exist_ok=True)
        store.save_local(str(self.index_path))

    def _buscar_faiss(self, consulta: str, k: int) -> str:
        embeddings = self._embeddings()
        store = FAISS.load_local(
            str(self.index_path),
            embeddings,
            allow_dangerous_deserialization=True,
        )
        result = retrieve_with_scores(store, consulta, k=min(k, max(len(self.listar()), 1)))
        if result.max_score < 0.20 or not result.chunks:
            return "No hay casos anteriores parecidos a esta consulta."
        bloques = []
        for indice, chunk in enumerate(result.chunks):
            confianza = result.scores[indice]
            bloques.append(f"[memoria | confianza={confianza:.2f}]\n{chunk}")
        return "\n\n".join(bloques)

    def _buscar_hash(self, consulta: str, k: int) -> str:
        consulta_vec = _hash_vec(consulta)
        ranked: list[tuple[float, dict]] = []
        for ticket in self.listar():
            nota = _nota(ticket)
            score = float(np.dot(consulta_vec, np.array(_hash_vec(nota), dtype=np.float32)))
            ranked.append((score, ticket))
        ranked.sort(key=lambda item: item[0], reverse=True)
        mejores = [item for item in ranked[:k] if item[0] >= 0.15]
        if not mejores:
            return "No hay casos anteriores parecidos a esta consulta."
        return "\n\n".join(
            f"[memoria | confianza={score:.2f}]\n{_nota(ticket)}" for score, ticket in mejores
        )

    def _siguiente_id(self) -> str:
        return f"TK-{len(self.listar()) + 1:04d}"


def _nota(ticket: dict) -> str:
    return (
        f"Ticket {ticket['ticket_id']} comercio {ticket['comercio']} "
        f"transaccion {ticket.get('transaction_id') or 'sin id'} estado {ticket['estado']}. "
        f"Consulta: {ticket['consulta']} Resumen: {ticket['resumen']} "
        f"Fuentes: {ticket.get('fuentes') or 'sin fuente'}"
    )


def _estado(valor: str) -> str:
    texto = _fold(valor)
    if "rechaz" in texto:
        return "rechazado"
    if "escal" in texto:
        return "escalado"
    return "resuelto"
