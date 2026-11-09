"""Interfaz Streamlit del agente VerifiPay."""

from __future__ import annotations

import streamlit as st

from src.agent import ask, build_agent_executor, messages_to_history, resumir_pasos
from src.config import LLM_API_KEY
from src.memory_store import MemoryStore

st.set_page_config(page_title="VerifiPay Bot Soporte", page_icon="💳", layout="wide")

st.title("VerifiPay — Agente de soporte")
st.caption("EP2 ISY0101 | Memoria, planificación y ticket de atención | Organización ficticia")

if not LLM_API_KEY:
    st.error("Configura LLM_API_KEY en el archivo .env antes de ejecutar la aplicación.")
    st.info("Copia `.env.example` a `.env` y agrega tu key de https://console.mistral.ai/api-keys")
    st.stop()

if "agent_executor" not in st.session_state:
    with st.spinner("Construyendo índices y agente..."):
        st.session_state.agent_executor = build_agent_executor()
    st.session_state.messages = []

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.subheader("Guion de la demo")
    examples = [
        "Soy de Ferretería Norte. Necesito el estado de TX-20250908-002 y cuándo depositan las ventas del fin de semana.",
        "Disculpa, el identificador era TX-99999999-000.",
        "¿Puedo enviarte el número de tarjeta del cliente por este chat?",
        "¿Qué quedó pendiente con Ferretería Norte?",
        "Mi terminal dice error E-204, ¿qué hago?",
    ]
    for example in examples:
        if st.button(example, use_container_width=True):
            st.session_state.pending_question = example

    if st.button("Reconstruir índices FAISS", use_container_width=True):
        with st.spinner("Reindexando..."):
            st.session_state.agent_executor = build_agent_executor(force_reindex=True)
        st.success("Índices reconstruidos.")

    st.divider()
    st.subheader("Memoria de largo plazo")
    tickets = MemoryStore().listar()
    if not tickets:
        st.caption("Todavía no hay tickets. El primero se escribe al cerrar una consulta.")
    for ticket in tickets[-4:]:
        st.caption(
            f"{ticket['ticket_id']} · {ticket['estado']} · {ticket['comercio']}"
        )

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Escribe la consulta del comercio...")
if "pending_question" in st.session_state:
    prompt = st.session_state.pop("pending_question")

if prompt:
    previos = list(st.session_state.messages)
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Consultando, planificando y registrando..."):
            try:
                result = ask(
                    st.session_state.agent_executor,
                    prompt,
                    chat_history=messages_to_history(previos),
                )
                answer = result.get("output", "No fue posible generar respuesta.")
                pasos = resumir_pasos(result)
            except Exception as exc:
                answer = f"Error al procesar la consulta: {exc}"
                pasos = []
        st.markdown(answer)
        if pasos:
            with st.expander("Herramientas usadas en este turno"):
                for paso in pasos:
                    st.text(paso)
        st.session_state.messages.append({"role": "assistant", "content": answer})
