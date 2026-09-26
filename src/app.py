"""Interfaz Streamlit del agente VerifiPay."""

from __future__ import annotations

import streamlit as st

from src.agent import ask, build_agent_executor
from src.config import LLM_API_KEY

st.set_page_config(page_title="VerifiPay Bot Soporte", page_icon="💳", layout="wide")

st.title("VerifiPay — Agente de Soporte con RAG")
st.caption("Caso académico EP1 ISY0101 | Organización ficticia")

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
    st.subheader("Consultas de ejemplo")
    examples = [
        "¿Cuándo me depositan las ventas del fin de semana?",
        "Mi terminal dice error E-204, ¿qué hago?",
        "¿Cuánto tengo para procesar una devolución?",
        "¿Puedo pedir el número de tarjeta del cliente por chat?",
        "Consulta el estado de TX-20250908-002",
    ]
    for example in examples:
        if st.button(example, use_container_width=True):
            st.session_state.pending_question = example

    if st.button("Reconstruir índices FAISS", use_container_width=True):
        with st.spinner("Reindexando..."):
            st.session_state.agent_executor = build_agent_executor(force_reindex=True)
        st.success("Índices reconstruidos.")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Escribe la consulta del comercio...")
if "pending_question" in st.session_state:
    prompt = st.session_state.pop("pending_question")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Consultando documentación..."):
            try:
                result = ask(st.session_state.agent_executor, prompt)
                answer = result.get("output", "No fue posible generar respuesta.")
            except Exception as exc:
                answer = f"Error al procesar la consulta: {exc}"
        st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})
