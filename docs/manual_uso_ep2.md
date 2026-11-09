# Manual de uso — Evaluación Parcial 2 (VerifiPay)

Sirve para ejecutar el agente y ver, en orden, las consultas de la defensa. El caso es el mismo de la Evaluación 1. Esta entrega agrega planificación, memoria y un ticket de escritura.

Hay dos formas de correrlo:

- **Sin modelo.** `demo_ep2.py` no gasta la API. Muestra el plan, la transacción, el ticket y la memoria. Úsala primero.
- **Con modelo.** Streamlit o `sesion_ep2.py`. Ahí el agente elige las herramientas y recuerda la conversación.

## 1. Preparar el entorno

Abre PowerShell en la carpeta del repositorio:

```powershell
cd "E:\ing soluciones\GITHUB\BOT_SOPORTE"
pip install -r requirements.txt
```

La clave va en `.env` (no se sube a GitHub):

```text
LLM_API_KEY=tu_key_de_mistral
```

La demo sin modelo funciona aunque la clave falle. Streamlit y la sesión no.

Índices documentales, solo la primera vez o si borraste `storage/`:

```powershell
python scripts/build_index.py
```

## 2. Demo sin modelo (empezar por aquí)

```powershell
python scripts/demo_ep2.py
```

Cada ejecución borra y vuelve a escribir `storage/demo_ep2`. No toca los tickets de Streamlit.

Qué debes ver, en este orden:

1. **Plan inicial.** Para Ferretería Norte y `TX-20250908-002` el orden es: consultar la transacción, buscar el manual, recuperar casos y registrar el ticket.
2. **Consulta.** La transacción sale pendiente, $48.900 CLP, débito. El plazo del fin de semana sigue siendo el del manual: martes antes de las 14:00.
3. **Escritura.** Aparece `Ticket TK-0001 registrado con estado resuelto`.
4. **Condición nueva.** `TX-99999999-000` no existe. El plan cambia a escalado y ya no informa un estado.
5. **Tarjeta.** Aunque el texto traiga un número, la salida dice `Rechazado` y la línea `¿El archivo contiene el PAN? False`.
6. **Memoria.** La pregunta por la ferretería y el débito recupera primero `TK-0001` con `TX-20250908-002`.

Si el paso 6 muestra primero el ticket de la transacción pendiente, la recuperación quedó bien.

## 3. Sesión con el modelo (memoria de corto plazo)

```powershell
python scripts/sesion_ep2.py
```

Escribe las consultas una por una. El programa guarda los últimos mensajes y se los pasa al turno siguiente. `salir` cierra.

Para recorrer las cuatro de una vez:

```powershell
python scripts/sesion_ep2.py --guion
```

Pega o deja que el guion use exactamente estas frases, en este orden:

1. `Soy de Ferretería Norte. Necesito el estado de TX-20250908-002 y cuándo depositan las ventas del fin de semana.`
2. `Disculpa, el identificador era TX-99999999-000.`
3. `¿Puedo enviarte el número de tarjeta del cliente por este chat?`
4. `¿Qué quedó pendiente con Ferretería Norte?`

Debajo de cada respuesta sale el bloque **Herramientas**. En un turno bien resuelto se ve `planificar_atencion` y, al cierre, `registrar_ticket`. En la segunda frase, si la API dice que no existe, debe aparecer `reevaluar_plan`. En la cuarta, `recuperar_contexto_casos`.

Esas cuatro consultas comparten la misma sesión. Si las lanzas con `run_agent.py`, cada una empieza de cero y la cuarta no puede recordar la ferretería.

Una consulta suelta, como en la Evaluación 1:

```powershell
python scripts/run_agent.py "Mi terminal dice error E-204, ¿qué hago?"
```

`--json` agrega la lista de herramientas usadas.

## 4. Interfaz para la defensa

```powershell
python -m streamlit run src/app.py
```

En el navegador, la barra lateral trae el mismo guion. Pulsa los botones de arriba hacia abajo, sin borrar la conversación entre uno y otro.

- El turno 2 habla de “el identificador”: el agente tiene los mensajes anteriores.
- El turno 4 pregunta qué quedó pendiente: tiene que leer los tickets, no el manual de la terminal.
- El desplegable **Herramientas usadas en este turno** es la traza para mostrar en la exposición.
- Abajo en la barra se listan los tickets de `storage/memoria`.

Los tickets de esta pantalla y los de `sesion_ep2.py` van al mismo archivo. Los de `demo_ep2.py` van a otra carpeta.

## 5. Dónde quedó escrito el caso

| Qué | Dónde |
|---|---|
| Tickets de Streamlit y de la sesión | `storage/memoria/tickets.jsonl` |
| Índice de esos tickets | `storage/memoria/faiss` |
| Corrida de práctica sin modelo | `storage/demo_ep2/tickets.jsonl` |
| Manual, políticas y norma | `data/` (no se reescriben) |

`storage/` no se sube a GitHub. Para vaciar la memoria de la interfaz, cierra Streamlit y borra la carpeta `storage/memoria`. La próxima consulta empieza sin tickets.

## 6. Pruebas que no gastan la API

```powershell
python -m pytest tests/test_memory_and_plan.py tests/test_data_and_api.py -v
```

Tienen que quedar en verde antes de la defensa. Comprueban el plan, el cambio cuando el identificador no existe, que el PAN no se guarda y que la ferretería se recupera.

El resto de `tests/` llama al modelo y pide `LLM_API_KEY`.

## 7. Si algo falla

- **Falta LLM_API_KEY.** Streamlit se detiene con ese aviso. Revisa `.env` o usa mientras tanto `python scripts/demo_ep2.py`.
- **HTTP 429.** El plan gratuito de Mistral limitó las consultas. Espera un minuto y repite solo la frase que falló, dentro de la misma sesión.
- **La cuarta pregunta no recuerda el caso.** La conversación se reinició, o el modelo no llamó a `registrar_ticket` en la primera. Vuelve a correr el guion desde la frase 1. La demo sin modelo igual deja `TK-0001` en `storage/demo_ep2` para mostrar la memoria.
- **Índice documental vacío.** `python scripts/build_index.py` y después abre de nuevo Streamlit.
