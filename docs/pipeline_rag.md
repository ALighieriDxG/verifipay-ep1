# Pipeline RAG — IE3

## Flujo de información

```mermaid
flowchart TD
    A[Documentos internos/externos] --> B[Loader]
    B --> C[RecursiveCharacterTextSplitter]
    C --> D[Embeddings mistral-embed]
    D --> E1[FAISS interno]
    D --> E2[FAISS externo]
    F[Consulta comercio] --> G[Agente LangChain]
    G --> H{Selección herramienta}
    H -->|Interna| E1
    H -->|Externa| E2
    H -->|Transacción| I[API Mock]
    E1 --> J[Contexto + scores]
    E2 --> J
    I --> J
    J --> K[LLM mistral-small-latest]
    K --> L[Respuesta + fuentes]
```

## Fuentes de datos

| Tipo | Archivos | Uso |
|---|---|---|
| Interno | manual, políticas, FAQ, tickets | Operativo/comercial |
| Externo | CMF, Ley 19.628, PCI-DSS | Normativo |

## Parámetros
- Chunk size: 350
- Overlap: 50
- Top-k: 3
- Vector store: FAISS (persistido en `storage/`)

## Integración interna + externa
El agente decide qué índice consultar según la naturaleza de la pregunta, cumpliendo IL1.2 del curso.
