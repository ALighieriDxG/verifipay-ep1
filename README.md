# VerifiPay Bot Soporte

Agente de soporte con **LangChain + RAG + function calling** para el caso ficticio **VerifiPay SpA** (EP1 — ISY0101).

## Contenido del repositorio

```
BOT_SOPORTE/
├── data/                  # Corpus simulado (interno + externo)
├── docs/                  # Análisis, arquitectura, prompts, guion presentación
├── scripts/               # build_index.py, run_agent.py
├── src/                   # Código fuente del agente
├── tests/                 # Pruebas unitarias, integración y evidencia
├── requirements.txt
└── .env.example
```

## Requisitos

- Python 3.10–3.13
- API key gratuita de Mistral: https://console.mistral.ai/api-keys

## Instalación

```bash
cd BOT_SOPORTE
pip install -r requirements.txt
copy .env.example .env    # Windows
# cp .env.example .env    # Linux/Mac
```

Edita `.env` y agrega tu key:

```
LLM_API_KEY=tu_key_aqui
```

## Ejecución

### 1. Construir índices FAISS (primera vez)

```bash
python scripts/build_index.py
```

### 2. Consulta por CLI

```bash
python scripts/run_agent.py "¿Cuándo me depositan las ventas del fin de semana?"
python scripts/run_agent.py "Consulta el estado de TX-20250908-002" --json
```

### 3. Interfaz web (recomendado para demo)

```bash
python -m streamlit run src/app.py
```

## Pruebas

```bash
python -m pytest tests/ -v
```

- **Unitarias:** cargan sin API key (`test_data_and_api.py`).
- **Integración/E2E:** requieren `LLM_API_KEY` en `.env`.

Ver resultados esperados en `tests/evidencia_pruebas.md`.

## Documentación técnica

| Documento | Contenido |
|---|---|
| `docs/analisis_caso.md` | Requerimientos organizacionales (IE1) |
| `docs/prompts.md` | Prompts y decisiones (IE2) |
| `docs/pipeline_rag.md` | Flujo RAG interno/externo (IE3) |
| `docs/arquitectura.md` | Diagrama y componentes (IE4/IE7) |
| `docs/presentacion.md` | Guion exposición 10 min (IE6–IE9) |

## Arquitectura resumida

1. **Ingesta:** documentos MD/JSON/CSV → chunking → embeddings `mistral-embed` → FAISS.
2. **Agente:** LangChain `create_openai_tools_agent` con 3 herramientas:
   - RAG interno (operativo/comercial)
   - RAG externo (normativo)
   - API mock de transacciones
3. **Salida:** respuesta en español con citas de fuente o escalamiento humano.

## Entrega EP1

En `entrega/` están el informe, la presentación HTML y el guion de la defensa.

## Caso organizacional

Organización ficticia del rubro fintech/pagos. Datos 100% simulados para uso académico.

## Declaración de uso de IA

Este repositorio fue desarrollado como entrega académica individual de Pablo Gutiérrez. Se utilizó IA generativa como apoyo para estructurar documentación y código base; el diseño técnico, las pruebas y las justificaciones fueron revisados por el estudiante. La reflexión individual del informe debe redactarse sin asistencia de IA.

## Referencias

- Lewis, P., et al. (2020). Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks.
- LangChain RAG: https://python.langchain.com/docs/tutorials/rag/
