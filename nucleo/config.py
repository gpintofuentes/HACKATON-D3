"""Configuración editable por los equipos, leída desde su Google Sheet.
La Sheet debe estar compartida como 'Cualquier persona con el vínculo: Lector'.
Formato esperado de la Sheet: columnas 'campo' y 'valor' (las demás se ignoran)."""

import re
import pandas as pd
import streamlit as st

LARGO_MAXIMO_DEFECTO = 1500  # caracteres por campo


PESTANA_CONFIG = "config"  # la app siempre lee la pestaña con este nombre


def _url_csv(url_sheet: str) -> str | None:
    """Convierte la URL de la Sheet en la URL CSV de la pestaña 'config'.
    Ignora qué pestaña estaba abierta cuando el equipo copió la URL."""
    m_id = re.search(r"/spreadsheets/d/([a-zA-Z0-9-_]+)", url_sheet)
    if not m_id:
        return None
    return (f"https://docs.google.com/spreadsheets/d/{m_id.group(1)}"
            f"/gviz/tq?tqx=out:csv&headers=1&sheet={PESTANA_CONFIG}")


@st.cache_data(ttl=20, show_spinner=False)
def _leer_sheet(url_csv: str) -> pd.DataFrame:
    return pd.read_csv(url_csv, dtype=str).fillna("")


def cargar_config(url_sheet: str, defectos: dict, largos: dict | None = None) -> tuple[dict, list[str]]:
    """Devuelve (configuración, avisos).
    - defectos: valores por defecto de cada campo (define qué campos existen).
    - largos: largo máximo por campo (opcional)."""
    largos = largos or {}
    avisos = []
    config = dict(defectos)

    url_csv = _url_csv(url_sheet)
    if not url_csv:
        return config, ["La URL no parece ser de una Google Sheet. Se usa la configuración por defecto."]

    try:
        df = _leer_sheet(url_csv)
    except Exception:
        return config, ["No se pudo leer la Sheet. Revisa que esté compartida como "
                        "'Cualquier persona con el vínculo'. Se usa la configuración por defecto."]

    df.columns = [c.strip().lower() for c in df.columns]
    if not {"campo", "valor"}.issubset(df.columns):
        return config, ["La Sheet no tiene las columnas 'campo' y 'valor'. "
                        "Se usa la configuración por defecto."]

    for _, fila in df.iterrows():
        campo = fila["campo"].strip()
        valor = fila["valor"].strip()
        if campo not in defectos:
            continue  # ignora campos desconocidos
        if not valor:
            avisos.append(f"El campo '{campo}' está vacío: se usa el valor por defecto.")
            continue
        maximo = largos.get(campo, LARGO_MAXIMO_DEFECTO)
        if len(valor) > maximo:
            avisos.append(f"El campo '{campo}' supera {maximo} caracteres: se recortó.")
            valor = valor[:maximo]
        config[campo] = valor

    return config, avisos


def panel_config(defectos: dict, largos: dict | None = None) -> dict:
    """Barra lateral: el equipo pega la URL de su Sheet y recarga la configuración."""
    with st.sidebar:
        st.header("Configuración del equipo")
        url = st.text_input("URL de la Google Sheet de tu equipo",
                            value=st.session_state.get("url_sheet", ""))
        st.session_state["url_sheet"] = url
        if st.button("🔄 Recargar configuración"):
            _leer_sheet.clear()

        if not url:
            st.caption("Sin Sheet: se usa la configuración por defecto.")
            return dict(defectos)

        config, avisos = cargar_config(url, defectos, largos)
        for a in avisos:
            st.warning(a)
        if not avisos:
            st.success("Configuración cargada.")
        return config
