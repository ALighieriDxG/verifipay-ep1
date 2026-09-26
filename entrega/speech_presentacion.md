# Speech — Defensa EP1 VerifiPay (10 minutos)

Pablo Gutiérrez · individual  
Abrir `presentacion_verifipay.html`, pulsar **Comenzar presentación** y dejar el avance automático apagado.  
Reloj de la esquina: 10:00 totales. Hablar mirando al docente, no leyendo la lámina.

Tiempo de reserva para la demo en vivo: al cierre, o si preguntan. Comandos:

```text
cd GITHUB/BOT_SOPORTE
python -m streamlit run src/app.py
```

Consultas para teclear, en este orden:

1. ¿Cuándo me depositan las ventas del fin de semana?
2. Mi terminal dice error E-204, ¿qué hago?
3. Consulta el estado de TX-20250908-002
4. ¿Puedo pedir el número de tarjeta del cliente por chat?

---

## Lámina 1 — Portada (0:00–0:35)

Buenos días. Soy Pablo Gutiérrez y esta es la Evaluación Parcial 1 de Ingeniería de Soluciones con IA.

El caso es VerifiPay SpA, una fintech ficticia chilena de medios de pago. El encargo es un agente de soporte que combina un modelo de lenguaje, recuperación aumentada y herramientas. El objetivo no es un chatbot que “sepa de pagos”. Es un canal que contesta con una fuente que se puede revisar, y que escala a una persona cuando esa fuente no existe.

Todo el corpus es simulado. El prototipo no está en producción.

## Lámina 2 — Recorrido (0:35–1:05)

En estos diez minutos voy a recorrer cuatro bloques.

Primero, el caso que ya aprobó el profesor: la organización, el problema y las metas medibles. Segundo, por qué la solución es un agente más un LLM más RAG, y no un modelo solo. Tercero, cómo quedó implementado: el prompt, el pipeline y la arquitectura. Cuarto, la coherencia entre el dato recuperado y la respuesta, las decisiones de diseño y la evidencia.

## Lámina 3 — Organización y problema (1:05–2:20)

VerifiPay tiene alrededor de 85 personas y 2.400 comercios. El soporte recibe cerca de 350 consultas al día, y una parte grande se repite.

El problema no es el volumen por sí solo. Es que cada consulta mezcla tres temas. Uno operativo: la terminal no conecta, el link de cobro venció, aparece el error E-204. Otro comercial: cuánto cobran por débito, cuándo depositan el fin de semana, cuántos días hay para una devolución. Y otro normativo: si se puede pedir el número de tarjeta, qué dice la Ley 19.628, qué exige PCI-DSS.

Hoy eso lo resuelve una persona buscando en manuales, en una FAQ y en un sistema de transacciones. Tres efectos. La primera respuesta se demora. Dos operadores pueden dar plazos distintos para la misma política. Y en temas sensibles —una comisión, un abono, un dato de tarjeta— un error no es solo mala atención: es un riesgo de cumplimiento. Además, cuando no hay evidencia, el escalamiento llega tarde.

## Lámina 4 — Objetivos y restricciones (2:20–3:15)

El caso aprobado trae cuatro metas, y el prototipo está armado para poder mostrarlas.

Primera respuesta en 15 minutos o menos. En el prototipo eso ocurre en segundos, porque la consulta no espera un turno humano. Segundo: al menos el 85 % de las respuestas con una fuente verificable. Por eso el prompt obliga a citar el archivo o el identificador de la transacción. Tercero: al menos el 40 % de las consultas frecuentes resueltas sin una persona. Eso lo cubre el manual, las políticas y el FAQ, que son justamente las preguntas que se repiten. Cuarto: si no hay evidencia, se escala. En el código eso es un umbral. Si el mejor fragmento queda bajo 0,35 de confianza, no se le pasa al modelo un contexto débil. Se le dice al comercio que lo vea un operador.

Las restricciones van en el mismo diseño. Español. Datos ficticios. No pedir RUT completo, número de tarjeta ni CVV. No inventar un plazo. Y el resumen normativo del prototipo no reemplaza la ley.

## Lámina 5 — Por qué agente, LLM y RAG (3:15–4:25)

Cada pieza tapa un fallo distinto.

RAG, recuperación aumentada, existe porque los plazos y las comisiones de VerifiPay no están en el entrenamiento del modelo. Lewis y colaboradores, en 2020, muestran que recuperar pasajes antes de generar mejora las tareas que dependen de conocimiento específico. Aquí el pasaje es el manual: las ventas de viernes, sábado y domingo se depositan el martes siguiente antes de las 14:00. Si el modelo contesta de memoria, puede decir “el lunes” y sonar convincente. Con RAG tiene que usar el fragmento.

El LLM existe porque el comercio no hace una búsqueda por palabra clave. Escribe como habla. El modelo entiende la pregunta y redacta una respuesta clara, pero solo a partir del contexto que recibió.

El agente existe porque no todas las preguntas van al mismo lugar. Una va al corpus interno. Otra a la normativa. Otra necesita el estado de una transacción, que no está en un documento: está en una API, que en el prototipo es un mock con tres registros. El agente elige la herramienta. Un pipeline fijo consultaría siempre todo, gastaría más contexto y mezclaría una norma de PCI con el manual de la terminal.

A la izquierda, el corpus interno: manual, políticas, glosario, FAQ y tickets. A la derecha, Ley 19.628, CMF, PCI-DSS, y las transacciones TX-20250908-001, 002 y TX-20250907-015.

## Lámina 6 — Prompts (4:25–5:25)

El prompt de sistema está en `src/prompts.py`. No es un “actúa como experto”. Tiene rol y reglas.

El rol es agente de soporte de comercios VerifiPay. Las reglas que defiendo son estas. Usar una herramienta antes de hablar de plazos, comisiones o normas. Cerrar citando la fuente. No inventar cifras. No pedir datos de tarjeta. Y, si la herramienta dice que no hay evidencia, escalar. No completar el hueco.

La temperatura está en 0,1 para que un mismo plazo no cambie de una ejecución a otra.

El enrutamiento no es un `if` que yo escribí por palabras clave. Son las descripciones de tres herramientas, y el modelo elige por function calling. `buscar_documentacion_interna` para operación y comercio. `buscar_normativa_externa` para datos personales, PCI y CMF. `consultar_estado_transaccion` cuando hay un ID. Eso se puede mostrar en la traza: se ve qué herramienta se llamó y con qué argumento.

El FAQ ayuda a la recuperación, porque ya trae la pregunta del comercio junto a la respuesta. Es un few-shot, pero puesto en el corpus, no solo en el prompt.

## Lámina 7 — Pipeline RAG (5:25–6:25)

El flujo de datos es este.

Se cargan Markdown, JSON y CSV, y cada pedazo guarda el nombre del archivo. Eso es lo que después se cita. El texto se parte en fragmentos de 350 caracteres, con 50 de solape. 350 es chico a propósito: el procedimiento del error E-204 cabe en un fragmento y no se mezcla con devoluciones o chargebacks.

Esos fragmentos se convierten en vectores con `mistral-embed`, el mismo proveedor del modelo de chat, y se guardan en dos índices FAISS. Uno interno y uno externo. Separarlos importa: si hubiera un solo índice, una pregunta sobre la terminal podría recuperar un párrafo de PCI y el modelo mezclaría los temas.

En la consulta se devuelven los tres fragmentos más cercanos. FAISS entrega distancia L2, donde menor es mejor. Yo la convierto en una confianza simple, uno dividido por uno más la distancia. Bajo 0,35, escalamiento.

La API no entra a FAISS. Si pregunto por TX-20250908-002, la función busca en un diccionario. Si el ID no está, dice que no está. No hay embedding que “se parezca” a una transacción inexistente.

## Lámina 8 — Arquitectura (6:25–7:35)

Esta es la lámina de arquitectura.

Arriba está el comercio, en Streamlit. Esa interfaz llama a un `AgentExecutor` de LangChain, armado con `create_openai_tools_agent`. El modelo todavía no redacta la respuesta final.

El agente tiene tres herramientas. RAG interno, RAG externo y la API mock. Las dos primeras leen su índice FAISS. La tercera lee las transacciones simuladas.

Solo entonces el modelo `mistral-small-latest` redacta. Recibe el contexto y las fuentes, y la salida vuelve al comercio. Si la herramienta ya devolvió el mensaje de escalamiento, la respuesta correcta es derivar, no estimar.

La historia del chat puede viajar en el turno siguiente, así que una repregunta no obliga a reindexar. Los índices se construyen una vez con `scripts/build_index.py` y quedan en disco.

En una frase: recuperar, decidir, y recién entonces redactar.

## Lámina 9 — Coherencia (7:35–8:40)

Aquí se ve la relación entre el dato y la respuesta. Cuatro casos, los mismos de la demo.

Primero. “¿Cuándo me depositan las ventas del fin de semana?” El manual y el FAQ dicen martes siguiente, antes de las 14:00. La respuesta tiene que repetir ese plazo y citar `manual_soporte.md` o `faq_comercios.json`. Si dice “en 48 horas” sin citar, falló, aunque suene razonable.

Segundo. Error E-204. El manual lo define como falla de conexión: revisar Wi-Fi, reiniciar, y si pasa de 30 minutos, escalar a nivel 2. La respuesta tiene que seguir ese procedimiento, no inventar un reset de fábrica.

Tercero. TX-20250908-002. No hay documento. La API responde pendiente, 48.900 pesos, débito, Ferretería Norte. La respuesta tiene que usar esos campos.

Cuarto. “¿Puedo pedir el número de tarjeta del cliente por chat?” El resumen PCI y la Ley 19.628 dicen que no se pide el PAN ni el CVV. Se usa el identificador de transacción. Aquí la fuente es el corpus externo, no el manual de abonos.

Eso es la credibilidad de la solución: se puede poner el fragmento al lado de la frase y ver si coinciden.

## Lámina 10 — Decisiones y evidencia (8:40–9:35)

Cada decisión está amarrada a un objetivo.

RAG y no solo el LLM, porque el modelo no conoce el martes a las 14:00 ni el 1,49 % más IVA del débito. Agente y no un pipeline fijo, porque la sesión cambia de tema. Dos índices, para que la norma no compita con la operación. Umbral 0,35, porque preferimos escalar antes que alucinar. API aparte, porque el estado de una transacción no vive en un PDF.

La evidencia que puedo mostrar ahora es concreta. Las pruebas unitarias de corpus y de la API pasan sin clave: `pytest tests/test_data_and_api.py`. TX-20250908-001 sale abonado y 125.000 pesos. Un ID inventado dice que no existe. Las pruebas del agente completo sí necesitan la clave de Mistral, y están en `tests/test_agent_integration.py`.

## Lámina 11 — Cierre (9:35–10:00)

Cierro con el criterio de diseño. O hay una fuente y se cita, o se escala. No hay una tercera opción en la que el modelo complete lo que no encontró.

El prototipo demuestra ese mecanismo. No demuestra todavía el 85 % sobre 350 consultas reales, porque VerifiPay y los documentos son ficticios. Tampoco certifica PCI ni reemplaza el texto de la ley. Eso queda dicho a propósito: es el límite del alcance académico.

Si hay tiempo, abro Streamlit y corro las cuatro consultas de la lámina de coherencia.

Quedo atento a las preguntas.

---

## Si preguntan

**¿Por qué 350 caracteres y no 1.000?**  
Para que un procedimiento quepa solo. Con chunks grandes, el error E-204 viaja pegado a devoluciones y el modelo mezcla plazos.

**¿Por qué dos índices y no un filtro de metadatos?**  
Un filtro también sirve. Dos índices hacen imposible que una búsqueda operativa devuelva PCI por similitud. En un prototipo chico, la separación física es más fácil de explicar y de probar.

**¿El 0,35 está medido?**  
Es un proxy, no una probabilidad calibrada. FAISS devuelve distancia, y 1/(1+distancia) solo ordena “qué tan lejos quedó el fragmento”. El número se puede ajustar con un set de preguntas etiquetadas. Hoy el valor está elegido para preferir el escalamiento.

**¿Y el 85 % y el 40 %?**  
Son metas del caso. El prototipo implementa la condición que las haría medibles: cita obligatoria y resolución automática de la FAQ. No hay un mes de tráfico real para calcular el porcentaje.

**¿Qué pasa si el modelo cita mal?**  
La herramienta ya le entrega el nombre del archivo. Si en la demo la cita no coincide con el fragmento, eso es un error del turno y se corrige el prompt o se muestra la traza de la herramienta. No se defiende una cita que el índice no devolvió.

**¿Usaste IA para el trabajo?**  
Sí, como apoyo para ordenar informe, láminas y guion. El caso, el corpus, los prompts y las pruebas están en el repositorio y los revisé yo. La reflexión individual del informe la escribo yo, sin IA, como pide la pauta.
