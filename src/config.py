"""Configuración central del proyecto VerifiPay Bot Soporte."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
INTERNAL_DIR = DATA_DIR / "internos"
EXTERNAL_DIR = DATA_DIR / "externos"
STORAGE_DIR = ROOT_DIR / "storage"

load_dotenv(ROOT_DIR / ".env")

LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.mistral.ai/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "mistral-small-latest")
EMBEDDING_MODEL = "mistral-embed"

CHUNK_SIZE = 350
CHUNK_OVERLAP = 50
TOP_K = 3
CONFIDENCE_THRESHOLD = 0.35

INTERNAL_INDEX_PATH = STORAGE_DIR / "faiss_internal"
EXTERNAL_INDEX_PATH = STORAGE_DIR / "faiss_external"
