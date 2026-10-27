"""Salvaguardas fijas: aviso de IA, ingreso por equipo y cuota de uso.
Este módulo NO debe ser modificado por los equipos."""

from threading import Lock
import streamlit as st

AVISO_IA = (
    "⚠️ **Esta herramienta usa inteligencia artificial.** "
    "Las respuestas pueden contener errores y no reemplazan el juicio humano. "
    "Revisa siempre las fuentes citadas. Todas las consultas quedan registradas."
)


def mostrar_aviso():
    """Aviso visible y permanente de uso de IA."""
    st.info(AVISO_IA)


def ingresar_equipo() -> str | None:
    """Pide código y clave del equipo. Devuelve el código si es válido."""
    if st.session_state.get("equipo"):
        return st.session_state["equipo"]

    st.subheader("Ingreso del equipo")
    codigo = st.text_input("Código del equipo (ej: E01)").strip().upper()
    clave = st.text_input("Clave del equipo", type="password").strip()

    if st.button("Ingresar"):
        equipos = st.secrets.get("equipos", {})
        if codigo in equipos and equipos[codigo] == clave:
            st.session_state["equipo"] = codigo
            st.rerun()
        else:
            st.error("Código o clave incorrectos.")
    return None


@st.cache_resource
def _contador():
    """Contador compartido entre todas las sesiones de esta app."""
    return {"usos": {}, "lock": Lock()}


def _limite() -> int:
    return int(st.secrets.get("CUOTA_POR_EQUIPO", 120))


def consumir_cuota(equipo: str) -> bool:
    """Descuenta una consulta. Devuelve False si el equipo agotó su cuota."""
    c = _contador()
    with c["lock"]:
        usados = c["usos"].get(equipo, 0)
        if usados >= _limite():
            return False
        c["usos"][equipo] = usados + 1
        return True


def cuota_restante(equipo: str) -> int:
    return max(_limite() - _contador()["usos"].get(equipo, 0), 0)
