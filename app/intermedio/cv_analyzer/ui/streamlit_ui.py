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


def renderizar_entradas():
    """Renderiza los controles de carga de CV, descripción del puesto y botones de acción."""
    col_cv, col_puesto = st.columns(2)

    with col_cv:
        st.subheader("1. Currículum del Candidato")
        archivo_cv = st.file_uploader(
            "Carga el CV en formato PDF",
            type=["pdf"],
            help="Solo se admiten archivos PDF con texto seleccionable.",
        )

    with col_puesto:
        st.subheader("2. Descripción del Puesto")
        descripcion_puesto = st.text_area(
            "Requisitos, habilidades y responsabilidades del puesto",
            height=200,
            placeholder=(
                "Puesto: Desarrollador Python\n"
                "Requisitos obligatorios: 3 años de experiencia, Python, APIs REST y PostgreSQL.\n"
                "Deseables: Docker, pruebas automatizadas y experiencia con LangChain.\n"
                "Responsabilidades: desarrollar servicios, integrar APIs y mantener pruebas."
            ),
        )

    col_btn_analizar, col_btn_limpiar, _ = st.columns([1, 1, 4])
    with col_btn_analizar:
        analizar_btn = st.button("Analizar Candidato", type="primary", use_container_width=True)
    with col_btn_limpiar:
        limpiar_btn = st.button("Limpiar", use_container_width=True)

    return archivo_cv, descripcion_puesto, analizar_btn, limpiar_btn

