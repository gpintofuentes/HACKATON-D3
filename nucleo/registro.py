"""Registro central: envía cada interacción al Google Form de la organización.
Este módulo es una salvaguarda: los equipos NO deben modificarlo."""

from datetime import datetime
import requests
import streamlit as st

# Identificadores de los campos del Form (no son secretos)
CAMPOS = {
    "fecha_hora": "entry.1474272147",
    "variante": "entry.649513176",
    "equipo": "entry.328284184",
    "entrada": "entry.433310011",
    "salida": "entry.515570122",
    "modo": "entry.1204640115",
}

LARGO_MAXIMO = 4000  # recorta textos muy largos para no exceder el Form


def registrar(variante: str, equipo: str, entrada: str, salida: str, modo: str) -> bool:
    """Envía una fila al registro. Devuelve True si se registró.
    Nunca interrumpe la app: si falla, solo avisa en consola."""
    datos = {
        CAMPOS["fecha_hora"]: datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        CAMPOS["variante"]: variante,
        CAMPOS["equipo"]: equipo,
        CAMPOS["entrada"]: str(entrada)[:LARGO_MAXIMO],
        CAMPOS["salida"]: str(salida)[:LARGO_MAXIMO],
        CAMPOS["modo"]: modo,
    }
    try:
        r = requests.post(st.secrets["REGISTRO_FORM_URL"], data=datos, timeout=5)
        return r.status_code == 200
    except Exception as e:
        print(f"[registro] fallo al registrar: {e}")
        return False
