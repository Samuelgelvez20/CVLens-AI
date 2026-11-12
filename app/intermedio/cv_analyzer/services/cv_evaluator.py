from langchain_openai import ChatOpenAI

from models.cv_model import AnalisisCV
from prompts.cv_prompts import crear_sistema_prompts


def crear_evaluador_cv():
    """Configura el modelo ChatOpenAI con salida estructurada AnalisisCV."""
    modelo_base = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.2,
    )
    modelo_estructurado = modelo_base.with_structured_output(AnalisisCV)
    chat_prompt = crear_sistema_prompts()
    return chat_prompt | modelo_estructurado


def evaluar_candidato(texto_cv: str, descripcion_puesto: str) -> AnalisisCV:
    """Invoca la cadena de evaluación y devuelve el análisis estructurado del candidato."""
    try:
        cadena_evaluacion = crear_evaluador_cv()
        resultado = cadena_evaluacion.invoke(
            {
                "texto_cv": texto_cv,
                "descripcion_puesto": descripcion_puesto,
            }
        )
        return resultado
    except Exception as exc:
        return AnalisisCV(
            nombre_candidato="Error en el análisis",
            experiencia_años=0,
            habilidades_clave=["No disponible"],
            education="No disponible",
            experiencia_relevante=f"No se pudo completar el análisis: {str(exc)}",
            fortalezas=["Requiere revisión manual"],
            areas_mejora=["Verificar configuración de API y formato del CV"],
            porcentaje_ajuste=0,
        )

