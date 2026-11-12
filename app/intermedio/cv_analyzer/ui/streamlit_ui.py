import streamlit as st

from models.cv_model import AnalisisCV
from services.cv_evaluator import evaluar_candidato
from services.pdf_processor import extraer_texto_pdf


def configurar_pagina() -> None:
    """Configura los metadatos y el título principal de la aplicación Streamlit."""
    st.set_page_config(
        page_title="Analizador de Currículums con IA",
        page_icon="📄",
        layout="wide",
    )
    st.title("📄 Analizador de Currículums con IA")
    st.markdown(
        "Compara un currículum en PDF con la descripción de un puesto "
        "y obtén un análisis estructurado del candidato."
    )


def renderizar_sidebar() -> None:
    """Muestra en la barra lateral los criterios de evaluación y recomendaciones de uso."""
    with st.sidebar:
        st.header("Criterios de Evaluación")
        st.markdown(
            """
            El modelo evalúa al candidato considerando los siguientes pesos orientativos:
            - **Experiencia relevante:** 40%
            - **Habilidades técnicas:** 35%
            - **Formación y certificaciones:** 15%
            - **Coherencia profesional:** 10%
            """
        )
        st.divider()
        st.info(
            "Sube un PDF con texto seleccionable. No se aplica OCR a documentos escaneados."
        )
