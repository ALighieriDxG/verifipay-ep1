# PORTADA

**Instituto Profesional Duoc UC**  
**Ingeniería de Soluciones con Inteligencia Artificial — ISY0101**

## Evaluación Parcial N°1
### Diseño de un agente de soporte con LLM y RAG

**Caso organizacional:** VerifiPay SpA (fintech ficticia chilena)  
**Estudiante:** Pablo Gutiérrez  
**Modalidad:** individual  
**Fecha:** septiembre de 2026  
**Repositorio:** https://github.com/ALighieriDxG/verifipay-ep1

---

La pauta pide un informe de **máximo cinco páginas** (Word o PDF). En la práctica de este documento, la portada, el índice, las referencias y los anexos van aparte de ese conteo. El cuerpo es la introducción más las secciones 1 a 6. Al pasarlo a Word: Times New Roman 12, interlineado 1,5, márgenes 2,5 cm. Si el cuerpo se pasa de cinco páginas, bajar el interlineado a 1,15 antes de recortar secciones. Insertar `arquitectura_verifipay.png` en la Figura 1. La reflexión individual (sección 7) se escribe a mano, sin IA.

---

# ÍNDICE

1. Introducción  
2. Propuesta del caso organizacional  
   2.1 Nombre y descripción de la organización  
   2.2 Problema y desafío  
   2.3 Objetivos de la intervención  
   2.4 Datos disponibles  
   2.5 Restricciones y requerimientos  
   2.6 Motivación para agentes, LLM y RAG  
   2.7 Referencias de viabilidad  
3. Análisis del caso y requerimientos de la solución (IE1)  
4. Formulación de prompts (IE2)  
5. Diseño e implementación del pipeline RAG (IE3)  
6. Arquitectura de la solución (IE4)  
7. Documentación técnica, decisiones y evidencia (IE5)  
8. Conclusiones  
9. Reflexión individual  
Referencias  
Anexos  

---

# 1. Introducción

Esta evaluación diseña e implementa un prototipo de agente de soporte para VerifiPay SpA. El problema no es “poner un chatbot”. El soporte mezcla preguntas operativas, comerciales y normativas, y hoy un operador debe buscar en manuales, políticas y sistemas distintos antes de responder. El resultado es lentitud, respuestas distintas para la misma política y riesgo de error en plazos, comisiones o datos de tarjeta.

La solución combina tres piezas. El **RAG** recupera fragmentos de un corpus interno y de un corpus normativo antes de redactar. El **LLM** entiende la pregunta en español y escribe la respuesta usando solo ese contexto. El **agente** elige la herramienta: documentación interna, normativa externa o una API simulada de transacciones. Si no hay evidencia suficiente, el sistema no completa el vacío: indica escalar a un operador.

El trabajo es académico. La organización y todos los datos son ficticios. El código, las pruebas y el README de ejecución están en el repositorio indicado en la portada. La defensa oral (IE6 a IE9) usa la presentación `presentacion_verifipay.html` y el cuaderno `demo_ep1.ipynb`; no forma parte del conteo de páginas de este informe.

# 2. Propuesta del caso organizacional

Esta sección reúne la documentación mínima exigida para evaluar la pertinencia y la viabilidad del caso. El docente ya aprobó esta propuesta; aquí queda integrada al informe para que el análisis técnico no quede desconectado del problema.

## 2.1 Nombre y breve descripción de la organización

VerifiPay SpA es una fintech ficticia chilena del rubro de pagos digitales. Procesa transacciones con tarjeta y transferencias para comercios minoristas y de servicios.

| Aspecto | Descripción |
|---|---|
| Rubro | Fintech / medios de pago |
| Tamaño | Cerca de 85 colaboradores y 2.400 comercios afiliados |
| Contexto | El soporte atiende abonos, comisiones, errores de terminal, cumplimiento y estado de transacciones |
| Volumen | Cerca de 350 consultas diarias, con alta repetición de preguntas operativas |

La organización no existe en el registro real de empresas. El tamaño, el volumen y el tipo de consultas se tomaron de situaciones habituales del sector para que el prototipo sea evaluable sin usar datos de clientes.

## 2.2 Identificación y descripción del problema

Los comercios preguntan por canales distintos y cada consulta puede mezclar tres temas: operación (plazos de abono, error de terminal, link de cobro), comercio (comisiones y políticas) y norma (protección de datos, PCI-DSS, lineamientos de la CMF). El proceso actual depende de personas que buscan en manuales, FAQ y sistemas internos.

Los problemas concretos son cuatro. La primera respuesta de las consultas repetitivas se demora. Dos operadores pueden dar plazos o comisiones distintas para la misma política. Es difícil juntar, en un solo mensaje, documentación interna, norma externa y el estado de una transacción. El escalamiento llega tarde, cuando ya se respondió sin evidencia.

El impacto es carga operativa del equipo, una peor experiencia para el comercio y error en temas sensibles. Un plazo o una comisión mal informados afectan la conciliación. Pedir un número de tarjeta por chat afecta el cumplimiento.

## 2.3 Objetivos de la intervención

| Objetivo | Indicador medible | Qué demuestra el prototipo |
|---|---|---|
| Automatizar la primera respuesta | ≤ 15 minutos | El canal automático responde en segundos |
| Respuestas fundamentadas | ≥ 85 % con fuente verificable | El prompt obliga a citar archivo o ID de transacción |
| Bajar la carga repetitiva | ≥ 40 % de consultas frecuentes sin humano | Manual, políticas y FAQ cubren esas preguntas |
| Escalar lo que no tiene evidencia | Derivación cuando no hay fuente | Si la confianza del fragmento es menor que 0,35, se recomienda un operador |

Estos porcentajes son metas de operación. El prototipo implementa el mecanismo que las haría medibles (cita, enrutamiento y abstención). No calcula el 85 % ni el 40 % sobre 350 consultas reales, porque no existe ese tráfico.

## 2.4 Datos disponibles o que se pueden obtener

Para el prototipo se simularon tres grupos de datos. En un despliegue real, las mismas fuentes podrían conectarse a la base documental y a las API de la organización.

**Corpus interno (operación y comercio):** `manual_soporte.md` (activación de terminal, error E-204, links de 72 horas, abonos, devoluciones y chargebacks), `politicas_comerciales.md` (comisión de débito 1,49 % + IVA, crédito 2,29 % + IVA, plazos), `faq_comercios.json` (pares pregunta–respuesta de las consultas repetidas), `glosario_fintech.md` y `tickets_resueltos.csv`.

**Corpus externo (norma):** resumen académico de la Ley N° 19.628, lineamientos aplicables de la CMF y resumen de PCI-DSS. Son resúmenes para el prototipo. No reemplazan el texto legal ni una certificación.

**Datos operacionales simulados:** API mock con tres transacciones. `TX-20250908-001` está abonada ($125.000 CLP, crédito, Café Central). `TX-20250908-002` está pendiente ($48.900 CLP, débito, Ferretería Norte). `TX-20250907-015` está devuelta. Un identificador que no está en el diccionario se informa como no encontrado.

Esos archivos se indexan con embeddings y FAISS, salvo la API, que se consulta por identificador exacto. Así el estado de una venta no se “parece” semánticamente a un párrafo del manual: o el ID existe, o no existe.

## 2.5 Restricciones o requerimientos particulares

- Cumplimiento: las respuestas sobre datos personales y seguridad de tarjeta se basan en el corpus normativo, no en el conocimiento general del modelo.
- Trazabilidad: toda respuesta cita la fuente (documento interno, norma o registro de transacción).
- Abstención: si no hay evidencia suficiente, el sistema lo dice y escala a un humano.
- Confidencialidad del prototipo: no hay datos reales de clientes ni de comercios.
- Idioma y tono: español, profesional, dirigido al comercio.
- Datos que no se piden: RUT completo, número de tarjeta (PAN) ni CVV.
- Alcance: prototipo académico. Quedan fuera las API productivas y la certificación PCI-DSS.

## 2.6 Motivación para el uso de agentes, LLM y RAG

| Tecnología | Por qué corresponde a este problema |
|---|---|
| RAG | Plazos, comisiones y normas son datos de VerifiPay, no del entrenamiento del modelo. Recuperar el fragmento antes de generar reduce la invención de cifras (Lewis et al., 2020). |
| LLM | El comercio escribe en lenguaje natural. El modelo entiende la pregunta y redacta una respuesta clara a partir del contexto recuperado. |
| Agente con herramientas | No todas las consultas van al mismo sitio. El agente elige RAG interno, RAG externo o la API mock, en lugar de un flujo rígido que consulte siempre todo. |
| Function calling | La consulta de transacciones queda como una llamada explícita, con el ID que se usó, y no como un texto inventado. |

Un modelo solo tendería a generalizar (“en 48 horas”). Un buscador por palabra clave no redacta ni combina dos fragmentos. Un pipeline fijo mezclaría PCI-DSS con el manual de la terminal. La arquitectura agente + LLM + RAG separa esas responsabilidades y permite abstenerse cuando la evidencia es débil.

## 2.7 Referencias o anexos relevantes

La viabilidad se apoya en el paper de RAG de Lewis et al. (2020), en la documentación de RAG de LangChain (2025) y en el corpus simulado del repositorio (`data/`, `docs/arquitectura.md`, `docs/pipeline_rag.md`). El detalle bibliográfico está en Referencias. Los anexos de este informe indican cómo ejecutar el sistema.

# 3. Análisis del caso y requerimientos de la solución (IE1)

A partir del caso aprobado, los requerimientos que la solución debe cumplir son estos:

1. Distinguir consultas operativas, comerciales, normativas y de estado de transacción.
2. Responder las repetitivas con una fuente que se pueda revisar.
3. No inventar montos, plazos ni procedimientos.
4. No solicitar datos de tarjeta en el chat.
5. Consultar el estado solo cuando hay un identificador de transacción.
6. Escalar cuando el fragmento recuperado no alcanza un umbral de confianza.
7. Dejar el mecanismo reproducible: código, README y pruebas.

La propuesta es viable en alcance académico porque el corpus ya está escrito, los identificadores de prueba son conocidos y el framework (LangChain + FAISS + un modelo compatible con la API de OpenAI) permite function calling sin integrar sistemas reales. La innovación del prototipo no está en el rubro, que es ficticio, sino en la separación de índices y en la regla de abstención: o hay fuente, o se escala.

# 4. Formulación de prompts (IE2)

El prompt de sistema vive en `src/prompts.py`. No es una instrucción genérica del tipo “actúa como experto”. Fija rol, reglas y enrutamiento.

Rol: agente de soporte de comercios adheridos a VerifiPay.

Reglas obligatorias:

1. Responder siempre en español, con tono profesional y claro.
2. Usar las herramientas antes de informar plazos, comisiones, errores o normativa.
3. Citar la fuente al final (por ejemplo, `Fuente: manual_soporte.md`).
4. No inventar montos, plazos ni procedimientos.
5. No solicitar RUT completo, números de tarjeta ni CVV.
6. Si la consulta trae un identificador, usar `consultar_estado_transaccion`.
7. Si no hay evidencia suficiente, indicar escalamiento a un operador humano.

El mismo prompt clasifica la consulta y la asocia a una herramienta: operación y comercio a `buscar_documentacion_interna`; norma (datos personales, PCI, CMF) a `buscar_normativa_externa`; estado de transacción a `consultar_estado_transaccion`. Las descripciones de esas herramientas funcionan como el criterio de enrutamiento. No se programó un `if` por palabras clave. El modelo elige por function calling y la llamada queda registrada.

Parámetros de control de contexto: temperatura 0,1, para que un plazo no cambie entre una ejecución y otra; tres fragmentos por recuperación; umbral de confianza 0,35, calculado como 1/(1 + distancia L2 de FAISS). Bajo ese umbral la herramienta no entrega un contexto débil: devuelve el mensaje de escalamiento. El FAQ aporta pares pregunta–respuesta. Eso acerca la consulta del comercio al fragmento correcto y cumple un papel similar al few-shot, puesto en el corpus y no solo en el prompt.

# 5. Diseño e implementación del pipeline RAG (IE3)

RAG consulta una base antes de generar. En tareas que dependen de un conocimiento concreto, eso disminuye respuestas que suenan bien y no están en la fuente (Lewis et al., 2020). El flujo implementado separa fuentes internas y externas, que es el requisito de combinar ambos tipos de datos.

**Ingesta.** `src/ingest.py` lee Markdown, el JSON del FAQ y el CSV de tickets. Cada documento conserva metadatos de fuente y de tipo (interno o externo). Ese nombre de archivo es lo que después se cita.

**Fragmentación.** `RecursiveCharacterTextSplitter` usa 350 caracteres y 50 de solapamiento. El tamaño es chico a propósito: el procedimiento del error E-204 cabe en un fragmento y no viaja pegado a devoluciones o chargebacks. Con fragmentos grandes, el modelo mezcla plazos de temas distintos.

**Embeddings e índices.** Los vectores se generan con `mistral-embed`, el mismo proveedor del modelo de chat, y se persisten en dos índices FAISS (Johnson et al., 2019): `faiss_internal` y `faiss_external`. Dos índices hacen que una pregunta operativa no recupere un párrafo de PCI-DSS solo porque ambas mencionan “tarjeta”. En la corrida de esta entrega el índice interno quedó en 24 vectores y el externo en 11. El script es `scripts/build_index.py`.

**Consulta.** El agente elige el índice. `src/rag.py` devuelve los tres fragmentos más cercanos, con nombre de archivo y una confianza derivada de la distancia L2 (menor distancia, mayor confianza). Ese bloque entra al modelo junto con la obligación de citar.

**Lo que no pasa por el índice.** La API mock (`src/api_mock.py`) busca el ID en un diccionario. Si no está, responde que no se encontró. No hay un embedding que “se parezca” a una transacción inexistente.

Evidencia de que los índices no se mezclan: la pregunta por el depósito de fin de semana recupera el FAQ y el manual, con confianza 0,81, y el fragmento dice martes siguiente antes de las 14:00. La pregunta por pedir el número de tarjeta recupera `pci_dss_resumen.md` y el resumen de la Ley 19.628, con confianza 0,74.

# 6. Arquitectura de la solución (IE4)

La arquitectura separa recuperación, procesamiento y generación. El comercio escribe en Streamlit (`src/app.py`) o en el cuaderno `demo_ep1.ipynb`. Esa entrada llama a un `AgentExecutor` de LangChain, armado con `create_openai_tools_agent`. El modelo todavía no redacta la respuesta final.

El agente tiene tres herramientas. El RAG interno y el RAG externo leen su índice FAISS. La API mock lee las transacciones simuladas. Solo entonces el modelo redacta, con el contexto y las fuentes, o indica escalamiento si la herramienta ya devolvió ese mensaje. La historia de chat puede viajar en un turno siguiente sin reconstruir los índices.

**Figura 1.** Flujo del agente VerifiPay: evidencia primero, redacción después. Insertar aquí `arquitectura_verifipay.png`.

```text
Comercio (Streamlit o cuaderno)
        → AgentExecutor (LangChain, temperatura 0,1)
        → Herramientas: RAG interno | RAG externo | API mock
        → Evidencia: FAISS interno | FAISS externo | diccionario de transacciones
        → LLM redacta con cita, o escala a un operador
```

| Módulo | Archivo | Responsabilidad |
|---|---|---|
| Ingesta e índices | `src/ingest.py`, `scripts/build_index.py` | Carga, corte, embeddings, FAISS |
| Recuperación | `src/rag.py` | Top-3, confianza y cita |
| Agente | `src/agent.py` | Elección de herramienta |
| Prompts | `src/prompts.py` | Rol, cita, abstención |
| Transacciones | `src/api_mock.py` | Estado por ID |
| Demo | `src/app.py`, `demo_ep1.ipynb` | Interfaz y recorrido celda por celda |

El modelo previsto en el diseño es `mistral-small-latest`. En la demostración se usó `ministral-8b-latest`, del mismo proveedor y con las mismas herramientas, porque el plan gratuito de `mistral-small-latest` respondió límite de consultas (HTTP 429). El cambio es de cupo del proveedor, no de arquitectura.

# 7. Documentación técnica, decisiones y evidencia (IE5)

Cada decisión de diseño está amarrada a un objetivo del caso.

| Decisión | Fundamento técnico | Objetivo que cubre |
|---|---|---|
| RAG y no solo LLM | El modelo no conoce el martes 14:00 ni el 1,49 % de débito | Fuente verificable (≥ 85 %) |
| Agente y no pipeline fijo | La misma sesión puede pedir un plazo y luego un ID | Enrutamiento |
| Dos índices FAISS | PCI-DSS no debe competir con el manual de terminal | Precisión por dominio |
| Chunk de 350 caracteres | Un procedimiento queda solo, sin arrastrar la sección vecina | Relevancia del fragmento |
| Umbral 0,35 | Mejor escalar que completar un hueco | Abstención |
| API fuera del índice | El estado no está en un documento; el ID o existe o no existe | Dato operacional |
| Temperatura 0,1 | Menos variación en cifras entre ejecuciones | Consistencia |
| `ministral-8b-latest` en la demo | El plan gratuito de `mistral-small-latest` respondió 429 | Poder mostrar el agente en vivo |

Las pruebas unitarias (`tests/test_data_and_api.py`) no requieren clave de API. Comprueban que cargan ambos corpus y que `TX-20250908-001` responde abonado y $125.000 CLP. Un ID inválido informa que no hay registro. Las pruebas de integración y de extremo a extremo (`tests/test_rag_integration.py`, `tests/test_agent_integration.py`) sí requieren `LLM_API_KEY`. Comprueban la recuperación del plazo del martes, la norma de la tarjeta, el procedimiento del error E-204 y el estado pendiente de `TX-20250908-002`.

La coherencia dato–respuesta, que se defiende en la presentación (IE6), se apoya en cuatro ejemplos del mismo corpus:

| Consulta | Evidencia | Respuesta que se defiende |
|---|---|---|
| ¿Cuándo depositan las ventas del fin de semana? | FAQ y `manual_soporte.md` | Martes siguiente, antes de las 14:00 |
| La terminal muestra error E-204 | `manual_soporte.md` | Falla de conexión: revisar Wi-Fi y reiniciar; si pasa de 30 minutos, nivel 2 |
| Estado de TX-20250908-002 | API mock | Pendiente, $48.900 CLP, débito, Ferretería Norte |
| ¿Puedo pedir la tarjeta del cliente por chat? | PCI-DSS y Ley 19.628 | No. No se pide PAN ni CVV. Se usa el ID de transacción |

El README del repositorio explica la instalación, la construcción de índices, la ejecución por cuaderno o por Streamlit y las pruebas. Con eso un evaluador puede repetir el prototipo sin depender de este informe.

# 8. Conclusiones

El prototipo cubre el caso aprobado: responde en lenguaje natural, fundamenta con corpus interno o normativo, consulta transacciones simuladas y se abstiene cuando la evidencia es débil. Los objetivos de 15 minutos, 85 % con fuente y 40 % sin humano quedan definidos como criterios de operación. Lo que esta entrega demuestra es el mecanismo —cita, enrutamiento y escalamiento—, no una medición sobre las 350 consultas diarias, porque la organización y los datos son ficticios.

Queda fuera de alcance conectar API productivas, certificar PCI-DSS y sustituir el texto de la ley por el resumen del corpus. Esos límites son parte del alcance académico y deben decirse en la defensa. Los indicadores IE6 a IE9 se exponen en las láminas de arquitectura, coherencia y decisiones (`presentacion_verifipay.html`), con el cuaderno como evidencia en vivo.

# 9. Reflexión individual

Completar a mano, sin asistencia de IA, antes de entregar (8 a 12 líneas). La pauta prohíbe redactar esta reflexión con IA.

Conviene cubrir: qué se aprendió al escribir el prompt y al separar los dos índices; qué decisión se defendería si preguntan por qué no basta un chatbot; qué límite del prototipo se reconoce (por ejemplo, el umbral 0,35 no es una probabilidad calibrada, o el cambio de modelo por el límite del plan gratuito).

______________________________________________________________________________

______________________________________________________________________________

______________________________________________________________________________

______________________________________________________________________________

# Referencias

Comisión para el Mercado Financiero. (s. f.). *Regulación y normativa*. https://www.cmfchile.cl/

Johnson, J., Douze, M. y Jégou, H. (2019). Billion-scale similarity search with GPUs. *IEEE Transactions on Big Data, 7*(3), 535–547. https://doi.org/10.1109/TBDATA.2019.2921572

LangChain. (2025). *Build a retrieval augmented generation (RAG) app*. https://python.langchain.com/docs/tutorials/rag/

Lewis, P., Perez, E., Piktus, A., Petroni, F., Karpukhin, V., Goyal, N., Küttler, H., Lewis, M., Yih, W., Rocktäschel, T., Riedel, S. y Kiela, D. (2020). Retrieval-augmented generation for knowledge-intensive NLP tasks. *Advances in Neural Information Processing Systems, 33*, 9459–9474.

Ley N° 19.628 de 1999. Sobre protección de la vida privada. Biblioteca del Congreso Nacional de Chile. https://www.bcn.cl/leychile/navegar?idNorma=141599

PCI Security Standards Council. (2024). *Payment Card Industry Data Security Standard: Requirements and testing procedures* (Version 4.0.1).

# Declaración de uso de inteligencia artificial

Se usó un asistente de IA generativa para ordenar la redacción de este informe, el apoyo visual de la presentación y el guion de exposición. El caso, el corpus simulado, los prompts, la arquitectura y las pruebas están en el repositorio y fueron revisados por el estudiante. La sección 9 debe completarse sin asistencia de IA. Citación de herramientas de IA según Biblioteca Duoc UC: https://bibliotecas.duoc.cl/ia

# Anexos

**Anexo A. Cómo ejecutar el prototipo.** En la carpeta del repositorio: instalar dependencias con `pip install -r requirements.txt`, completar `LLM_API_KEY` en `.env` (no se sube a GitHub), construir índices con `python scripts/build_index.py` y abrir `demo_ep1.ipynb`. Las celdas se ejecutan de arriba hacia abajo. La celda del agente usa `ministral-8b-latest`.

**Anexo B. Figura de arquitectura.** Archivo `arquitectura_verifipay.png`, junto a este informe. Es la Figura 1 de la sección 6.

**Anexo C. Evidencia de pruebas.** `tests/evidencia_pruebas.md` y los archivos `tests/test_*.py`.

**Anexo D. Defensa oral.** `presentacion_verifipay.html` (lámina 8 arquitectura, IE7; lámina 9 coherencia, IE6; lámina 10 decisiones y evidencia, IE8 e IE9) y `speech_presentacion.md`.
