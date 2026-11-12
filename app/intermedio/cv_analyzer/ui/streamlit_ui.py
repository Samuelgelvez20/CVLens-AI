import csv
import io
import json
import streamlit as st

from models.cv_model import AnalisisCV
from services.cv_evaluator import EvaluacionError, evaluar_candidato, limitar_texto_cv
from services.database import (
    extraer_titulo_vacante,
    guardar_analisis_en_bd,
    inicializar_bd,
    listar_analisis_por_vacante,
    listar_vacantes,
    obtener_vacante_por_id,
)
from services.pdf_processor import extraer_texto_pdf


def inicializar_estado() -> None:
    """Inicializa las claves necesarias en st.session_state."""
    valores_por_defecto = {
        "uploader_key": 0,
        "vacante_titulo_input": "",
        "vacante_desc_input": "",
        "ultimo_resultado": None,
        "mensaje_guardado": False,
    }
    for clave, valor in valores_por_defecto.items():
        if clave not in st.session_state:
            st.session_state[clave] = valor


def limpiar_formulario() -> None:
    """Limpia los campos del formulario y el resultado actual antes de instanciar widgets."""
    st.session_state["vacante_titulo_input"] = ""
    st.session_state["vacante_desc_input"] = ""
    st.session_state["ultimo_resultado"] = None
    st.session_state["mensaje_guardado"] = False
    st.session_state["uploader_key"] += 1


def cargar_vacante_en_formulario(titulo: str, descripcion: str) -> None:
    """Carga una vacante del historial en el formulario principal."""
    st.session_state["vacante_titulo_input"] = titulo
    st.session_state["vacante_desc_input"] = descripcion


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
    """Muestra los criterios de evaluación y el historial de vacantes guardadas."""
    with st.sidebar:
        with st.expander("Criterios de Evaluación", expanded=False):
            st.markdown(
                """
                El modelo evalúa al candidato considerando los siguientes pesos orientativos:
                - **Experiencia relevante:** 40%
                - **Habilidades técnicas:** 35%
                - **Formación y certificaciones:** 15%
                - **Coherencia profesional:** 10%
                """
            )
            st.caption(
                "Sube un PDF con texto seleccionable. No se aplica OCR a documentos escaneados."
            )

        st.divider()
        st.header("🗂️ Historial de Análisis")

        try:
            vacantes = listar_vacantes()
        except Exception:
            st.warning("No se pudo cargar el historial en este momento.")
            return

        if not vacantes:
            st.caption("Aún no hay análisis guardados. Analiza un CV y pulsa Guardar Análisis.")
            return

        for vacante in vacantes:
            with st.container(border=True):
                st.markdown(f"**{vacante['titulo']}**")
                st.caption(f"{vacante['total_cvs']} CV(s) guardado(s)")

                extracto = " ".join(vacante["descripcion"].split())
                if len(extracto) > 90:
                    extracto = extracto[:87] + "..."
                st.caption(extracto)

                col_v, col_c = st.columns(2)
                with col_v:
                    if st.button(
                        "Ver vacante",
                        key=f"ver_vacante_{vacante['id']}",
                        use_container_width=True,
                    ):
                        mostrar_dialogo_vacante(vacante["id"])
                with col_c:
                    if st.button(
                        "Ver CVs",
                        key=f"ver_cvs_{vacante['id']}",
                        use_container_width=True,
                    ):
                        mostrar_dialogo_cvs(vacante["id"])


def renderizar_entradas():
    """Renderiza los controles de carga de CV, descripción del puesto y botones de acción."""
    col_cv, col_puesto = st.columns(2)

    with col_cv:
        st.subheader("1. Currículum del Candidato")
        archivo_cv = st.file_uploader(
            "Carga el CV en formato PDF",
            type=["pdf"],
            key=f"cv_uploader_{st.session_state['uploader_key']}",
            help="Solo se admiten archivos PDF con texto seleccionable.",
        )

    with col_puesto:
        st.subheader("2. Descripción del Puesto")
        titulo_vacante = st.text_input(
            "Nombre de la vacante (opcional)",
            key="vacante_titulo_input",
            placeholder="Ej. Desarrollador Backend Python Junior",
        )
        descripcion_puesto = st.text_area(
            "Requisitos, habilidades y responsabilidades del puesto",
            height=175,
            key="vacante_desc_input",
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
        st.button("Limpiar", on_click=limpiar_formulario, use_container_width=True)

    return archivo_cv, titulo_vacante, descripcion_puesto, analizar_btn


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


def renderizar_detalle_analisis(resultado: AnalisisCV) -> None:
    """Muestra las métricas, perfil, habilidades, fortalezas y áreas de mejora."""
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


def generar_csv_candidatos(analisis_lista: list[dict]) -> str:
    """Genera un archivo CSV en memoria con el ranking de candidatos de una vacante."""
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "Candidato",
            "Archivo PDF",
            "Porcentaje Ajuste",
            "Evaluación",
            "Recomendación",
            "Años Experiencia",
            "Educación",
            "Habilidades Clave",
        ]
    )
    for item in analisis_lista:
        porcentaje = item["porcentaje_ajuste"]
        writer.writerow(
            [
                item["nombre_candidato"],
                item["nombre_archivo_pdf"],
                f"{porcentaje}%",
                obtener_evaluacion_principal(porcentaje),
                obtener_recomendacion_final(porcentaje),
                item["experiencia_anos"],
                item["education"],
                ", ".join(item["habilidades_clave"]),
            ]
        )
    return buffer.getvalue()


@st.dialog("Enunciado completo de la vacante", width="large")
def mostrar_dialogo_vacante(vacante_id: int) -> None:
    """Muestra el enunciado completo de una vacante en un diálogo modal."""
    vacante = obtener_vacante_por_id(vacante_id)
    if not vacante:
        st.warning("No se encontró la vacante seleccionada.")
        return

    st.subheader(vacante["titulo"])
    st.text_area(
        "Enunciado guardado",
        value=vacante["descripcion"],
        height=260,
        disabled=True,
        label_visibility="collapsed",
    )
    st.button(
        "Cargar en el formulario",
        on_click=cargar_vacante_en_formulario,
        args=(vacante["titulo"], vacante["descripcion"]),
        use_container_width=True,
    )


@st.dialog("CVs aplicados a la vacante", width="large")
def mostrar_dialogo_cvs(vacante_id: int) -> None:
    """Muestra el ranking, exportación y detalle de los CVs guardados para una vacante."""
    vacante = obtener_vacante_por_id(vacante_id)
    if not vacante:
        st.warning("No se encontró la vacante seleccionada.")
        return

    st.subheader(vacante["titulo"])
    analisis_lista = listar_analisis_por_vacante(vacante["id"])
    if not analisis_lista:
        st.info("Todavía no hay CVs guardados para esta vacante.")
        return

    tabla_resumen = [
        {
            "Candidato": item["nombre_candidato"],
            "Archivo": item["nombre_archivo_pdf"],
            "Ajuste (%)": item["porcentaje_ajuste"],
            "Evaluación": obtener_evaluacion_principal(item["porcentaje_ajuste"]),
            "Recomendación": obtener_recomendacion_final(item["porcentaje_ajuste"]),
            "Experiencia (años)": item["experiencia_anos"],
        }
        for item in analisis_lista
    ]
    st.dataframe(tabla_resumen, use_container_width=True, hide_index=True)

    col_csv, col_json = st.columns(2)
    with col_csv:
        st.download_button(
            label="Exportar CSV",
            data=generar_csv_candidatos(analisis_lista),
            file_name=f"candidatos_vacante_{vacante['id']}.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with col_json:
        st.download_button(
            label="Exportar JSON",
            data=json.dumps(analisis_lista, ensure_ascii=False, indent=2, default=str),
            file_name=f"candidatos_vacante_{vacante['id']}.json",
            mime="application/json",
            use_container_width=True,
        )

    for idx, item in enumerate(analisis_lista, start=1):
        etiqueta = (
            f"#{idx} — {item['nombre_candidato']} | "
            f"{item['porcentaje_ajuste']}% ({obtener_recomendacion_final(item['porcentaje_ajuste'])}) | "
            f"{item['nombre_archivo_pdf']}"
        )
        with st.expander(etiqueta, expanded=(idx == 1)):
            modelo_item = AnalisisCV(
                nombre_candidato=item["nombre_candidato"],
                experiencia_años=item["experiencia_anos"],
                habilidades_clave=item["habilidades_clave"],
                education=item["education"],
                experiencia_relevante=item["experiencia_relevante"],
                fortalezas=item["fortalezas"],
                areas_mejora=item["areas_mejora"],
                porcentaje_ajuste=item["porcentaje_ajuste"],
            )
            renderizar_detalle_analisis(modelo_item)


def mostrar_resultados(resultado_state: dict) -> None:
    """Presenta el resultado del último análisis y permite guardarlo en el historial."""
    st.divider()
    st.subheader("Resultados del Análisis")

    if resultado_state.get("truncado"):
        st.info(
            "El documento era muy extenso y se analizó su contenido principal para agilizar la evaluación."
        )

    renderizar_detalle_analisis(resultado_state["analisis"])

    if resultado_state.get("guardado"):
        st.success("Análisis guardado en el historial de la vacante.")
    else:
        if st.button("Guardar Análisis", type="secondary"):
            try:
                guardar_analisis_en_bd(
                    titulo_vacante=resultado_state["titulo"],
                    descripcion_vacante=resultado_state["descripcion"],
                    nombre_archivo_pdf=resultado_state["nombre_archivo"],
                    analisis=resultado_state["analisis"],
                )
                resultado_state["guardado"] = True
                st.session_state["ultimo_resultado"] = resultado_state
                st.session_state["mensaje_guardado"] = True
                st.rerun()
            except Exception:
                st.error(
                    "No se pudo guardar el análisis en la base de datos. Inténtalo nuevamente."
                )


def main() -> None:
    """Punto de entrada principal de la interfaz de Streamlit."""
    inicializar_bd()
    inicializar_estado()
    configurar_pagina()
    renderizar_sidebar()

    archivo_cv, titulo_vacante, descripcion_puesto, analizar_btn = renderizar_entradas()

    if analizar_btn:
        if not archivo_cv or not descripcion_puesto.strip():
            st.warning(
                "Por favor, carga un CV en PDF y escribe la descripción del puesto antes de analizar."
            )
        else:
            with st.spinner("Extrayendo texto del PDF..."):
                texto_cv = extraer_texto_pdf(archivo_cv)

            if texto_cv.startswith("Error"):
                st.error(
                    "No se pudo leer el contenido del PDF. Asegúrate de que sea un archivo válido con texto seleccionable."
                )
            else:
                texto_cv_seguro, fue_truncado = limitar_texto_cv(texto_cv)
                with st.spinner("Analizando candidato con IA..."):
                    try:
                        resultado = evaluar_candidato(texto_cv_seguro, descripcion_puesto)
                        titulo_final = (
                            titulo_vacante.strip() or extraer_titulo_vacante(descripcion_puesto)
                        )
                        st.session_state["ultimo_resultado"] = {
                            "analisis": resultado,
                            "titulo": titulo_final,
                            "descripcion": descripcion_puesto.strip(),
                            "nombre_archivo": archivo_cv.name,
                            "truncado": fue_truncado,
                            "guardado": False,
                        }
                        st.session_state["mensaje_guardado"] = False
                    except EvaluacionError as err:
                        st.error(str(err))

    if st.session_state.get("ultimo_resultado"):
        mostrar_resultados(st.session_state["ultimo_resultado"])
