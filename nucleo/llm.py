"""Conexión con OpenAI: salida JSON estructurada, reintentos y modo demo.
Este módulo NO debe ser modificado por los equipos."""

import json
import time
from pathlib import Path

import streamlit as st
from openai import (OpenAI, RateLimitError, APIConnectionError,
                    APITimeoutError, InternalServerError)

REINTENTOS = 3
ERRORES_TRANSITORIOS = (RateLimitError, APIConnectionError,
                        APITimeoutError, InternalServerError)
CARPETA_DATOS = Path(__file__).resolve().parent.parent / "datos"


@st.cache_resource
def _cliente() -> OpenAI:
    # max_retries=0: los reintentos los controlamos nosotros
    return OpenAI(api_key=st.secrets["OPENAI_API_KEY"], timeout=40, max_retries=0)


@st.cache_data
def _demo(variante: str) -> dict:
    ruta = CARPETA_DATOS / f"demo_{variante.lower()}.json"
    try:
        return json.loads(ruta.read_text(encoding="utf-8"))
    except Exception:
        return {}


def respuesta_demo(variante: str, clave: str, respaldo: dict) -> dict:
    """Busca una respuesta precalculada; si no existe, usa el respaldo genérico."""
    return _demo(variante).get(clave, respaldo)


def consultar(sistema: str, usuario: str, esquema: dict, nombre_esquema: str,
              variante: str, clave_demo: str, respaldo_demo: dict) -> tuple[dict, str]:
    """Devuelve (respuesta, modo). modo = 'real' o 'demo'.
    - sistema: instrucciones del prompt (reglas fijas + campos del equipo).
    - usuario: lo que escribió el usuario.
    - esquema: JSON Schema que la respuesta debe cumplir."""

    # Modo demo forzado desde los secrets (contingencia manual)
    if str(st.secrets.get("MODO_DEMO", "no")).lower() == "si":
        return respuesta_demo(variante, clave_demo, respaldo_demo), "demo"

    modelo = st.secrets.get("MODELO")
    if not modelo:
        st.error("Falta configurar el modelo (MODELO) en los secrets.")
        return respuesta_demo(variante, clave_demo, respaldo_demo), "demo"

    for intento in range(REINTENTOS):
        try:
            r = _cliente().chat.completions.create(
                model=modelo,
                messages=[{"role": "system", "content": sistema},
                          {"role": "user", "content": usuario}],
                response_format={
                    "type": "json_schema",
                    "json_schema": {"name": nombre_esquema, "schema": esquema, "strict": True},
                },
            )
            return json.loads(r.choices[0].message.content), "real"
        except ERRORES_TRANSITORIOS as e:
            print(f"[llm] intento {intento + 1} falló: {type(e).__name__}")
            time.sleep(2 ** intento)  # espera 1, 2, 4 segundos
        except Exception as e:
            print(f"[llm] error no recuperable: {e}")
            break

    st.warning("El servicio de IA no respondió. Se muestra una respuesta de demostración.")
    return respuesta_demo(variante, clave_demo, respaldo_demo), "demo"
