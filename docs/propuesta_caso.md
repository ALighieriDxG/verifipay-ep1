# Propuesta de caso — Chatbot de soporte VerifiPay

**Proyecto:** VerifiPay Bot Soporte  
**Asignatura:** Ingeniería de Soluciones con Inteligencia Artificial  
**Alcance:** Propuesta de idea (prototipo académico)

---

## 1. Nombre y breve descripción de la organización

**VerifiPay SpA** es una fintech ficticia chilena del rubro de pagos digitales. Procesa transacciones con tarjeta y transferencias para comercios minoristas y de servicios.

| Aspecto | Descripción |
|---|---|
| **Rubro** | Fintech / medios de pago |
| **Tamaño** | ~85 colaboradores; ~2.400 comercios afiliados |
| **Contexto** | El equipo de soporte atiende consultas de comercios sobre abonos, comisiones, errores de terminal, cumplimiento normativo y estado de transacciones. El volumen estimado es de ~350 consultas diarias, con alta repetición de preguntas operativas. |

La organización es ficticia, pero el contexto y los problemas reflejan situaciones habituales en empresas reales del sector.

---

## 2. Identificación y descripción del problema / desafío

Los comercios contactan a soporte por múltiples canales con preguntas que combinan información operativa (plazos de abono, comisiones), comercial (políticas del servicio) y normativa (protección de datos, PCI-DSS). Hoy el proceso depende en gran medida de agentes humanos que buscan respuestas en manuales, FAQs y sistemas internos.

**Problemas concretos:**

- Tiempos de primera respuesta elevados en consultas repetitivas.
- Riesgo de respuestas inconsistentes cuando distintos agentes interpretan la misma política.
- Dificultad para combinar en una sola respuesta documentación interna, normativa externa y datos de transacciones en tiempo (casi) real.
- Escalamiento tardío cuando no hay evidencia suficiente para responder con certeza.

**Impacto:** mayor carga operativa del equipo de soporte, experiencia deficiente para el comercio y riesgo de errores en temas sensibles (plazos, comisiones, cumplimiento normativo).

---

## 3. Objetivos de la intervención

| Objetivo | Indicador |
|---|---|
| Automatizar la primera respuesta en consultas frecuentes | Primera respuesta ≤ 15 min (en prototipo: segundos) |
| Asegurar respuestas fundamentadas | ≥ 85 % de respuestas con fuente documental verificable |
| Reducir carga en consultas repetitivas | ≥ 40 % de consultas frecuentes resueltas sin intervención humana |
| Escalar correctamente casos complejos | Derivación a agente humano cuando no hay evidencia suficiente |

---

## 4. Datos disponibles o que se pueden obtener

Para el prototipo académico se simularán los siguientes datos:

**Corpus interno (operativo/comercial):**
- Manual de soporte (`manual_soporte.md`)
- Políticas comerciales (`politicas_comerciales.md`)
- FAQ de comercios (`faq_comercios.json`)
- Glosario fintech (`glosario_fintech.md`)
- Historial de tickets resueltos (`tickets_resueltos.csv`)

**Corpus externo (normativo):**
- Resumen Ley 19.628 (protección de datos)
- Normativa CMF aplicable
- Resumen PCI-DSS

**Datos operacionales simulados:**
- API mock de consulta de transacciones (estado, montos, códigos de error)

Estos datos se indexan con embeddings y búsqueda vectorial (FAISS) para alimentar el componente RAG. En un despliegue real, las mismas fuentes podrían conectarse a bases documentales y APIs productivas de la organización.

---

## 5. Restricciones o requerimientos particulares

- **Cumplimiento normativo:** las respuestas sobre datos personales y seguridad deben basarse en fuentes normativas verificables, no en conocimiento general del modelo.
- **Trazabilidad:** toda respuesta debe citar la fuente utilizada (documento interno, norma o registro de transacción).
- **No alucinar:** si no hay evidencia suficiente, el bot debe indicarlo y escalar a un agente humano.
- **Confidencialidad:** en el prototipo no se usan datos reales de clientes ni comercios; todo el corpus es simulado.
- **Idioma:** respuestas en español, tono profesional orientado a comercios.
- **Alcance académico:** solución prototipo, no productiva; integración con sistemas reales queda fuera de scope.

---

## 6. Motivación para el uso de agentes de IA, LLMs y RAG

| Tecnología | Por qué es adecuada |
|---|---|
| **RAG (Retrieval-Augmented Generation)** | Las consultas de soporte requieren datos actualizados y específicos de VerifiPay (plazos, comisiones, políticas). Un LLM solo tiende a inventar o generalizar; RAG recupera fragmentos reales del corpus y los usa como contexto verificable. |
| **LLM** | Permite entender preguntas en lenguaje natural, redactar respuestas claras y combinar información de varias fuentes en un mismo mensaje. |
| **Agente con herramientas** | No todas las consultas son iguales: algunas requieren documentación interna, otras normativa externa y otras consultar el estado de una transacción. Un agente decide qué herramienta usar (RAG interno, RAG externo o API mock), en lugar de un flujo rígido predefinido. |
| **Function calling** | Habilita la integración controlada con sistemas operacionales (consulta de transacciones) manteniendo trazabilidad de lo que el agente consultó. |

En conjunto, la arquitectura agente + RAG + LLM equilibra flexibilidad conversacional con precisión y auditabilidad, requisitos críticos en soporte fintech.

---

## 7. Referencias o anexos relevantes

**Referencias bibliográficas:**
- Lewis, P., et al. (2020). *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*. NeurIPS.
- Documentación LangChain RAG: https://python.langchain.com/docs/tutorials/rag/

**Anexos del repositorio (desarrollo posterior a esta propuesta):**
- `docs/analisis_caso.md` — Análisis detallado del caso
- `docs/arquitectura.md` — Diagrama y componentes técnicos
- `docs/pipeline_rag.md` — Flujo de ingesta y recuperación
- `data/` — Corpus simulado interno y externo

**Stack previsto (prototipo):** Python, LangChain, Mistral (LLM + embeddings), FAISS, Streamlit (interfaz de demo).

---

*Documento preparado como propuesta de idea para evaluación de pertinencia y viabilidad del caso. Los datos y la organización son ficticios con fines académicos.*
