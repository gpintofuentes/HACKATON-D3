"""Configuración editable por los equipos, leída desde su Google Sheet.
La Sheet debe estar compartida como 'Cualquier persona con el vínculo: Lector'.
- Pestaña 'config': columnas 'campo' y 'valor' (las demás se ignoran).
- Pestañas extra ('casos_extra', 'leyes_extra'): filas que se suman al corpus."""

import re
import pandas as pd
import streamlit as st

PESTANA_CONFIG = "config"     # la app siempre lee la pestaña con este nombre
LARGO_MAXIMO_DEFECTO = 1500   # caracteres por campo de configuración


def _url_csv(url_sheet: str, pestana: str = PESTANA_CONFIG) -> str | None:
    """Convierte la URL de la Sheet en la URL CSV de una pestaña, por su nombre.
    Ignora qué pestaña estaba abierta cuando el equipo copió la URL."""
    m_id = re.search(r"/spreadsheets/d/([a-zA-Z0-9-_]+)", url_sheet)
    if not m_id:
        return None
    return (f"https://docs.google.com/spreadsheets/d/{m_id.group(1)}"
            f"/gviz/tq?tqx=out:csv&headers=1&sheet={pestana}")


@st.cache_data(ttl=20, show_spinner=False)
def _leer_sheet(url_csv: str) -> pd.DataFrame:
    return pd.read_csv(url_csv, dtype=str).fillna("")


def _normalizar_columnas(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).strip().lower() for c in df.columns]
    return df


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
        df = _normalizar_columnas(_leer_sheet(url_csv))
    except Exception:
        return config, ["No se pudo leer la Sheet. Revisa que esté compartida como "
                        "'Cualquier persona con el vínculo'. Se usa la configuración por defecto."]

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


def leer_pestana(pestana: str, columnas: list[str]) -> tuple[pd.DataFrame | None, str | None]:
    """Lee una pestaña extra de la Sheet del equipo.
    Devuelve (datos, aviso). datos = None si no hay Sheet o no se pudo leer.
    Si la pestaña no existe, Google entrega la primera pestaña sin avisar:
    por eso se verifica que estén las columnas esperadas."""
    url = st.session_state.get("url_sheet", "")
    if not url:
        return None, None  # sin Sheet: no hay filas extra, y no es un error

    url_csv = _url_csv(url, pestana)
    if not url_csv:
        return None, None  # el aviso de URL inválida ya lo muestra el panel

    try:
        df = _normalizar_columnas(_leer_sheet(url_csv))
    except Exception:
        return None, f"No se pudo leer la pestaña '{pestana}'."

    faltantes = [c for c in columnas if c not in df.columns]
    if faltantes:
        return None, (f"No encontramos la pestaña '{pestana}' con las columnas esperadas. "
                      "Revisa que exista y que no hayan cambiado los encabezados.")
    return df[columnas], None


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
