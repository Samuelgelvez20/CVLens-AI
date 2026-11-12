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


def obtener_evaluacion_principal(porcentaje: int) -> str:
    """Devuelve la etiqueta de evaluación principal según el porcentaje de ajuste."""
    if porcentaje >= 80:
        return "Excelente"
    if porcentaje >= 60:
        return "Bueno"
    if porcentaje >= 40:
        return "Regular"
    return "Bajo"


def obtener_recomendacion_final(porcentaje: int) -> str:
    """Devuelve la recomendación final de contratación según el porcentaje de ajuste."""
    if porcentaje >= 70:
        return "Candidato recomendado"
    if porcentaje >= 50:
        return "Candidato con potencial"
    return "Candidato no recomendado"


def mostrar_resultados(resultado: AnalisisCV) -> None:
    """Presenta en la interfaz el análisis estructurado del candidato."""
    st.divider()
    st.subheader("Resultados del Análisis")

    evaluacion = obtener_evaluacion_principal(resultado.porcentaje_ajuste)
    recomendacion = obtener_recomendacion_final(resultado.porcentaje_ajuste)

    col_metrica, col_estado = st.columns(2)
    with col_metrica:
        st.metric(
            label="Porcentaje de Ajuste",
            value=f"{resultado.porcentaje_ajuste}%",
            delta=evaluacion,
        )
        st.progress(resultado.porcentaje_ajuste / 100)
    with col_estado:
        st.markdown("### Recomendación Final")
        if resultado.porcentaje_ajuste >= 70:
            st.success(recomendacion)
        elif resultado.porcentaje_ajuste >= 50:
            st.warning(recomendacion)
        else:
            st.error(recomendacion)

    st.markdown("### Perfil del Candidato")
    col_info1, col_info2, col_info3 = st.columns(3)
    with col_info1:
        st.markdown(f"**Nombre:** {resultado.nombre_candidato}")
    with col_info2:
        st.markdown(f"**Experiencia:** {resultado.experiencia_años} años")
    with col_info3:
        st.markdown(f"**Educación:** {resultado.education}")

    st.markdown("**Experiencia Relevante:**")
    st.write(resultado.experiencia_relevante)

    st.markdown("### Habilidades Clave")
    st.write(", ".join(resultado.habilidades_clave))

    col_fort, col_mejora = st.columns(2)
    with col_fort:
        st.markdown("### Fortalezas")
        for fortaleza in resultado.fortalezas:
            st.markdown(f"- {fortaleza}")

    with col_mejora:
        st.markdown("### Áreas de Mejora")
        for area in resultado.areas_mejora:
            st.markdown(f"- {area}")

    if st.button("Guardar Análisis"):
        st.info("Funcionalidad en desarrollo: el almacenamiento de análisis aún no está disponible.")


def main() -> None:
    """Punto de entrada principal de la interfaz de Streamlit."""
    configurar_pagina()
    renderizar_sidebar()

    archivo_cv, descripcion_puesto, analizar_btn, limpiar_btn = renderizar_entradas()

    if limpiar_btn:
        st.rerun()

    if analizar_btn:
        if not archivo_cv or not descripcion_puesto.strip():
            st.warning(
                "Por favor, carga un CV en PDF y escribe la descripción del puesto antes de analizar."
            )
            return

        with st.spinner("Extrayendo texto del PDF..."):
            texto_cv = extraer_texto_pdf(archivo_cv)

        if texto_cv.startswith("Error"):
            st.error(texto_cv)
            return

        with st.spinner("Analizando candidato con IA..."):
            resultado = evaluar_candidato(texto_cv, descripcion_puesto)

        mostrar_resultados(resultado)



