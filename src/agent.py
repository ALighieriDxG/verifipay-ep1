"""Agente LangChain con herramientas RAG y API mock."""

from __future__ import annotations

import time

from langchain_classic.agents import AgentExecutor, create_openai_tools_agent, tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from src.api_mock import consultar_transaccion
from src.config import CONFIDENCE_THRESHOLD, LLM_API_KEY, LLM_BASE_URL, LLM_MODEL
from src.ingest import ensure_indexes
from src.prompts import ESCALATION_MESSAGE, SYSTEM_PROMPT
from src.rag import format_citations, retrieve_with_scores


def _require_api_key() -> None:
    if not LLM_API_KEY:
        raise ValueError(
            "Falta LLM_API_KEY. Copia .env.example a .env y agrega tu key de Mistral."
        )


def build_tools(internal_store, external_store):
    @tool
    def buscar_documentacion_interna(consulta: str) -> str:
        """Busca procedimientos, políticas comerciales, FAQ y tickets de soporte internos de VerifiPay."""
        result = retrieve_with_scores(internal_store, consulta)
        if result.max_score < CONFIDENCE_THRESHOLD:
            return ESCALATION_MESSAGE
        return (
            f"Contexto interno recuperado (confianza={result.max_score:.2f}):\n"
            f"{result.context}\n\nFuentes: {format_citations(result)}"
        )

    @tool
    def buscar_normativa_externa(consulta: str) -> str:
        """Busca normativa CMF, Ley 19.628 y resumen PCI-DSS aplicable al soporte."""
        result = retrieve_with_scores(external_store, consulta)
        if result.max_score < CONFIDENCE_THRESHOLD:
            return ESCALATION_MESSAGE
        return (
            f"Contexto normativo recuperado (confianza={result.max_score:.2f}):\n"
            f"{result.context}\n\nFuentes: {format_citations(result)}"
        )

    @tool
    def consultar_estado_transaccion(transaction_id: str) -> str:
        """Consulta el estado de una transacción VerifiPay por ID (ej: TX-20250908-001)."""
        return consultar_transaccion(transaction_id)

    return [
        buscar_documentacion_interna,
        buscar_normativa_externa,
        consultar_estado_transaccion,
    ]


def build_agent_executor(force_reindex: bool = False, model: str | None = None) -> AgentExecutor:
    _require_api_key()
    internal_store, external_store = ensure_indexes(force=force_reindex)

    llm = ChatOpenAI(
        base_url=LLM_BASE_URL,
        api_key=LLM_API_KEY,
        model=model or LLM_MODEL,
        temperature=0.1,
    )

    tools = build_tools(internal_store, external_store)
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder("chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder("agent_scratchpad"),
        ]
    )

    agent = create_openai_tools_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=False, handle_parsing_errors=True)


def _is_rate_limit(exc: Exception) -> bool:
    text = str(exc).lower()
    return "429" in text or "rate limit" in text or "rate_limited" in text


def ask(agent_executor: AgentExecutor, question: str, chat_history: list | None = None) -> dict:
    payload = {"input": question}
    if chat_history:
        payload["chat_history"] = chat_history
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            return agent_executor.invoke(payload)
        except Exception as exc:
            if not _is_rate_limit(exc) or attempt == 2:
                raise
            last_error = exc
            time.sleep(3 * (attempt + 1))
    raise last_error  # pragma: no cover
